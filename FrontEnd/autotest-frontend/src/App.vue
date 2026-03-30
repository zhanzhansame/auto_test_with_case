<template>
  <div style="min-height: 100vh; background-color: #f0f2f5; padding: 20px; box-sizing: border-box;">
    
    <div :style="{ 
           maxWidth: '1200px', 
           margin: '0 auto', 
           marginTop: parsedModules.length === 0 ? '15vh' : '20px',
           transition: 'margin-top 0.4s ease-in-out' 
         }">
      
      <h2 style="margin-bottom: 30px; color: #303133; text-align: center;">AutoTest测试平台调试版</h2>

      <el-row :gutter="20" justify="center">
        
        <el-col :span="parsedModules.length > 0 ? 10 : 14">
          <DocumentInput 
            v-model="markdownContent" 
            :loading="isParsing"
            @on-parse="handleParse" 
          />
        </el-col>

        <el-col :span="14" v-if="parsedModules.length > 0">
          <el-card class="box-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: flex-end; gap: 10px; flex-wrap: wrap;">
              <el-button type="primary" plain @click="downloadParsedMarkdown">导出需求 Markdown</el-button>
              <el-button type="primary" plain @click="downloadParsedCsv">导出需求 Excel</el-button>
              <el-button type="success" @click="downloadTestCasesCsv" :disabled="!hasGeneratedCases">下载测试用例 Excel</el-button>
              <el-button type="success" plain @click="downloadTestCasesMarkdown" :disabled="!hasGeneratedCases">
                下载测试用例 Markdown
              </el-button>
            </div>
          </el-card>
          <ModuleTable 
            :modules="parsedModules" 
            @on-generate="handleGenerate" 
          />
          <PointsPreview 
            :modules="parsedModules"
            @on-delete-case="deleteTestCase"
            @on-delete-module="deleteModule"
            @on-update-case="updateCaseField"
          />
        </el-col>
        
      </el-row>
    </div>
  </div>
</template>

<script setup>
import DocumentInput from './components/DocumentInput.vue'
import ModuleTable from './components/ModuleTable.vue'
import PointsPreview from './components/PointsPreview.vue'
import { useTestEngine } from './composables/useTestEngine'

const { 
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
} = useTestEngine()
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>