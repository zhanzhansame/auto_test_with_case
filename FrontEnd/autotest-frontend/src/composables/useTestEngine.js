import { computed, ref } from 'vue'
import { parseDocumentApi, uploadDocumentApi, generatePointsApi, exportRequirementsApi, exportTestCasesApi } from '../api'
import { ElMessage } from 'element-plus'

const downloadBlob = (content, filename, type) => {
  const blob = new Blob([content], { type })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

const downloadResponseFile = (response, fallbackFilename) => {
  const blob = new Blob([response.data], { type: response.data.type || 'application/octet-stream' })
  let filename = fallbackFilename
  const disposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
  if (disposition) {
    const filenameMatch = disposition.match(/filename\*=UTF-8''(.+)|filename="?([^";]+)"?/)
    if (filenameMatch) {
      filename = decodeURIComponent(filenameMatch[1] || filenameMatch[2])
    }
  }
  downloadBlob(blob, filename, blob.type)
}

const normalizeTestCase = (rawCase, index) => ({
  case_id: rawCase.case_id || `C${index + 1}`,
  case_name: rawCase.case_name || rawCase.name || `用例 ${index + 1}`,
  preconditions: rawCase.preconditions || rawCase.pre_condition || rawCase.precondition || '',
  summary: rawCase.summary || rawCase.description || '',
  steps: Array.isArray(rawCase.steps) ? rawCase.steps : [],
  expected_results: Array.isArray(rawCase.expected_results) ? rawCase.expected_results : [],
})

export function useTestEngine() {
  const markdownContent = ref('')
  const parsedModules = ref([])
  const isParsing = ref(false)

  const hasGeneratedCases = computed(() => {
    return parsedModules.value.some((m) => (Array.isArray(m.testCases) && m.testCases.length > 0) || (Array.isArray(m.testPoints) && m.testPoints.length > 0))
  })

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

  // 生成测试点逻辑
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

        moduleData.testCases = cases.length ? cases.map((c, idx) => normalizeTestCase(c, idx)) : null
        moduleData.testPoints = cases.length ? moduleData.testCases.map((c) => c.case_name).filter(Boolean) : (payload.testpoint?.[functionName] || [])
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

  const updateCaseField = (moduleIndex, caseIndex, field, value) => {
    const moduleItem = parsedModules.value[moduleIndex]
    if (!moduleItem || !moduleItem.testCases || !moduleItem.testCases[caseIndex]) return
    if (field === 'steps' || field === 'expected_results') {
      moduleItem.testCases[caseIndex][field] = value
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line)
    } else {
      moduleItem.testCases[caseIndex][field] = value
    }
  }

  const deleteTestCase = (moduleIndex, caseIndex) => {
    const moduleItem = parsedModules.value[moduleIndex]
    if (!moduleItem || !moduleItem.testCases) return
    moduleItem.testCases.splice(caseIndex, 1)
  }

  const deleteModule = (moduleIndex) => {
    parsedModules.value.splice(moduleIndex, 1)
  }

  const downloadParsedMarkdown = async () => {
    if (!parsedModules.value.length) {
      ElMessage.warning('当前没有可导出的需求内容')
      return
    }
    try {
      const response = await exportRequirementsApi(parsedModules.value, 'md')
      downloadResponseFile(response, 'parsed_requirements.md')
    } catch (error) {
      console.error(error)
      ElMessage.error('导出需求 Markdown 失败，请检查后端接口')
    }
  }

  const downloadParsedCsv = async () => {
    if (!parsedModules.value.length) {
      ElMessage.warning('当前没有可导出的需求内容')
      return
    }
    try {
      const response = await exportRequirementsApi(parsedModules.value, 'xlsx')
      downloadResponseFile(response, 'parsed_requirements.xlsx')
    } catch (error) {
      console.error(error)
      ElMessage.error('导出需求 Excel 失败，请检查后端接口')
    }
  }

  const downloadTestCasesCsv = async () => {
    if (!hasGeneratedCases.value) {
      ElMessage.warning('当前没有可下载的测试用例')
      return
    }
    try {
      const response = await exportTestCasesApi(parsedModules.value, 'xlsx')
      downloadResponseFile(response, 'test_cases.xlsx')
    } catch (error) {
      console.error(error)
      ElMessage.error('下载测试用例 Excel 失败，请检查后端接口')
    }
  }

  const downloadTestCasesMarkdown = async () => {
    if (!hasGeneratedCases.value) {
      ElMessage.warning('当前没有可下载的测试用例')
      return
    }
    try {
      const response = await exportTestCasesApi(parsedModules.value, 'md')
      downloadResponseFile(response, 'test_cases.md')
    } catch (error) {
      console.error(error)
      ElMessage.error('下载测试用例 Markdown 失败，请检查后端接口')
    }
  }

  return {
    markdownContent,
    parsedModules,
    isParsing,
    hasGeneratedCases,
    handleParse,
    handleGenerate,
    updateCaseField,
    deleteTestCase,
    deleteModule,
    downloadParsedMarkdown,
    downloadParsedCsv,
    downloadTestCasesCsv,
    downloadTestCasesMarkdown
  }
}