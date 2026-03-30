import { ref } from 'vue'
import { parseDocumentApi, uploadDocumentApi, generatePointsApi } from '../api'
import { ElMessage } from 'element-plus'

export function useTestEngine() {
  const markdownContent = ref('')
  const parsedModules = ref([])
  const isParsing = ref(false)

  // 接收从 DocumentInput 传来的 Payload
  const handleParse = async (payload) => {
    isParsing.value = true
    try {
      let response;
      
      // 路由：根据输入模式调用不同的后端接口
      if (payload.mode === 'text') {
        response = await parseDocumentApi(payload.content)
      } else if (payload.mode === 'file') {
        response = await uploadDocumentApi(payload.file)
      }

      // 统一处理返回结果 (假设你后端的返回结构是一致的)
      if (response && response.data.status === 'success') {
        parsedModules.value = response.data.data.map(item => ({
          ...item,
          loading: false,
          testPoints: null,
          testCases: null
        }))
        ElMessage.success(`成功解析出 ${parsedModules.value.length} 个功能模块`)
      } else {
         const err = response?.data?.error
         ElMessage.error(err?.message || err || '后端解析失败')
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('服务请求异常，请检查 Flask 后台日志')
    } finally {
      isParsing.value = false
    }
  }

  // 生成测试点逻辑 (保持不变)
  const handleGenerate = async (moduleData, index) => {
    if (!moduleData || !moduleData.content) {
      ElMessage.warning('该模块缺少可用于生成的内容')
      return
    }

    const moduleName = moduleData.level2_module && moduleData.level2_module !== '无'
      ? moduleData.level2_module
      : (moduleData.level1_module || '未知模块')

    const functionName = moduleData.level3_function && moduleData.level3_function !== '无'
      ? moduleData.level3_function
      : (moduleData.level2_module || '未知功能点')

    moduleData.loading = true
    moduleData.testPoints = null
    moduleData.testCases = null

    try {
      const response = await generatePointsApi(moduleData.content, moduleName, functionName)
      if (response && response.data && response.data.status === 'success') {
        const payload = response.data.data || {}
        // 新 prompt：{ test_cases: [ { case_id, case_name, steps, ... } ] }
        // 旧格式：{ testpoint: { "<function>": ["验证xxx", ...] } }
        let cases = []
        if (Array.isArray(payload.test_cases) && payload.test_cases.length) {
          cases = payload.test_cases
        } else if (payload.testpoint?.[functionName]?.length) {
          cases = payload.testpoint[functionName].map((name) => ({
            case_name: name,
            steps: [],
            expected_results: []
          }))
        }
        moduleData.testCases = cases.length ? cases : null
        moduleData.testPoints = cases.length
          ? cases.map((c) => c.case_name).filter(Boolean)
          : (payload.testpoint?.[functionName] || [])
        const count = cases.length || moduleData.testPoints.length
        ElMessage.success(`已为 ${functionName} 生成 ${count} 条测试用例`)
      } else {
        const err = response?.data?.error
        ElMessage.error(err?.message || err || '后端生成失败')
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('生成测试点请求失败，请检查 Flask 后台日志')
    } finally {
      moduleData.loading = false
    }
  }

  return {
    markdownContent,
    parsedModules,
    isParsing,
    handleParse,
    handleGenerate
  }
}