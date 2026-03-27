<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: bold;">1. 输入需求文档</span>
        <el-button type="primary" :loading="loading" @click="handleTriggerParse">
          解析文档结构
        </el-button>
      </div>
    </template>

    <el-tabs v-model="inputMode" class="demo-tabs">
      <el-tab-pane label="文本粘贴" name="text">
        <el-input
          :model-value="modelValue"
          @update:model-value="$emit('update:modelValue', $event)"
          type="textarea"
          :rows="18"
          placeholder="请在此粘贴 Markdown 格式的需求文档..."
        />
      </el-tab-pane>

      <el-tab-pane label="Markdown/PDF 上传" name="file">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="onFileChange"
          :on-remove="onFileRemove"
          :on-exceed="handleExceed"
          accept=".md,.markdown,.pdf"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将 Markdown/PDF 文件拖到此处，或 <em>点击选择</em>
          </div>
          <template #tip>
            <div class="el-upload__tip" style="color: #E6A23C;">
              注意：仅支持单文件上传。重新上传会覆盖当前文件。
            </div>
          </template>
        </el-upload>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: String,
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'on-parse'])

// 控制当前是文本模式还是文件模式
const inputMode = ref('text')
// 暂存选中的文件
const selectedFile = ref(null)

// 捕获文件选择事件
const onFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw
}

// 捕获文件移除事件
const onFileRemove = () => {
  selectedFile.value = null
}

// 处理超出文件数量限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先移除当前文件后再选择')
}

// 点击顶部“解析文档结构”按钮时的分发逻辑
const handleTriggerParse = () => {
  if (inputMode.value === 'text') {
    if (!props.modelValue.trim()) {
      ElMessage.warning('请输入需求文档内容')
      return
    }
    emit('on-parse', { mode: 'text', content: props.modelValue })
  } else {
    if (!selectedFile.value) {
      ElMessage.warning('请先选择一个 Markdown 或 PDF 文件')
      return
    }
    emit('on-parse', { mode: 'file', file: selectedFile.value })
  }
}
</script>