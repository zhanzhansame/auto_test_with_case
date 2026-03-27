<template>
  <el-card class="box-card" v-if="hasPoints">
    <template #header>
      <div class="card-header" style="font-weight: bold;">
        <span>3. 测试点预览</span>
      </div>
    </template>
    <div v-for="(module, index) in modules" :key="index">
      <div v-if="module.testPoints && module.testPoints.length > 0" style="margin-bottom: 20px; padding: 10px; background-color: #f5f7fa; border-radius: 4px;">
        <h4 style="color: #409EFF; margin-top: 0; margin-bottom: 10px;">{{ module.level3_function || module.level2_module }}</h4>
        <ul style="padding-left: 20px; margin: 0; line-height: 1.8;">
          <li v-for="(point, pIndex) in module.testPoints" :key="pIndex">{{ point }}</li>
        </ul>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  modules: Array
})
const hasPoints = computed(() => {
  return props.modules.some(m => m.testPoints && m.testPoints.length > 0)
})
</script>