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
          <ModuleTable 
            :modules="parsedModules" 
            @on-generate="handleGenerate" 
          />
          <PointsPreview 
            :modules="parsedModules" 
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
  handleParse, 
  handleGenerate 
} = useTestEngine()
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>