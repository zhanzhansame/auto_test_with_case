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
  // 字段名必须与后端一致（Flask: request.files.get("file")）
  formData.append('file', file)

  // 注意：axios 会自动正确设置 multipart boundary，不建议手动强设 Content-Type
  return apiClient.post('/analyze_file', formData)
}

// 3. 生成测试点接口 (保持不变)
export const generatePointsApi = (content, moduleName, functionName) => {
  return apiClient.post('/generate_points', {
    content,
    module: moduleName,
    function: functionName
  })
}