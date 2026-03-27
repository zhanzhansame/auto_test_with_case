import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 60000 // 解析 PDF 可能比较慢，建议把超时时间拉长到 60 秒
})

// 1. 原有的纯文本解析接口
export const parseDocumentApi = (content) => {
  return apiClient.post('/analyze_document', { content })
}

// 2. 新增的文件上传解析接口
export const uploadDocumentApi = (file) => {
  const formData = new FormData()
  formData.append('file', file) // 这里的 'file' 要和后端接口接收的字段名一致
  
  return apiClient.post('/analyze_document_file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 3. 生成测试点接口 (保持不变)
export const generatePointsApi = (content, moduleName, functionName) => {
  return apiClient.post('/generate_points', {
    content,
    module: moduleName,
    function: functionName
  })
}