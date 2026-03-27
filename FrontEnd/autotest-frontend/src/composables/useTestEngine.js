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
          testPoints: null
        }))
        ElMessage.success(`成功解析出 ${parsedModules.value.length} 个功能模块`)
      } else {
         ElMessage.error(response?.data?.error || '后端解析失败')
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
     // ... 保持原有代码 ...
  }

  return {
    markdownContent,
    parsedModules,
    isParsing,
    handleParse,
    handleGenerate
  }
}