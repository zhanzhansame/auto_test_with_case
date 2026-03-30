<template>
  <el-card class="box-card" v-if="hasPoints">
    <template #header>
      <div class="card-header" style="font-weight: bold;">
        <span>3. 测试用例预览</span>
      </div>
    </template>
    <div v-for="(module, index) in modules" :key="index">
      <!-- 新接口：结构化 test_cases -->
      <div
        v-if="module.testCases && module.testCases.length > 0"
        style="margin-bottom: 20px; padding: 10px; background-color: #f5f7fa; border-radius: 4px;"
      >
        <h4 style="color: #409EFF; margin-top: 0; margin-bottom: 10px;">
          {{ module.level3_function || module.level2_module }}
        </h4>
        <div
          v-for="(tc, tcIndex) in module.testCases"
          :key="tc.case_id || tcIndex"
          style="margin-bottom: 16px; padding: 12px; background: #fff; border-radius: 4px; border: 1px solid #ebeef5;"
        >
          <div style="font-weight: 600; margin-bottom: 8px;">
            {{ tc.case_name || '未命名用例' }}
            <span v-if="tc.case_id" style="color: #909399; font-weight: normal; font-size: 12px; margin-left: 8px;">
              {{ tc.case_id }}
            </span>
          </div>
          <p v-if="tc.preconditions" style="margin: 6px 0; font-size: 13px; color: #606266;">
            <strong>前置：</strong>{{ tc.preconditions }}
          </p>
          <p v-if="tc.summary" style="margin: 6px 0; font-size: 13px; color: #606266;">
            <strong>摘要：</strong>{{ tc.summary }}
          </p>
          <div v-if="tc.steps && tc.steps.length" style="margin-top: 8px;">
            <strong style="font-size: 13px;">步骤：</strong>
            <ol style="margin: 6px 0 0 0; padding-left: 20px; line-height: 1.8;">
              <li v-for="(s, si) in tc.steps" :key="si">{{ s }}</li>
            </ol>
          </div>
          <div v-if="tc.expected_results && tc.expected_results.length" style="margin-top: 8px;">
            <strong style="font-size: 13px;">预期：</strong>
            <ol style="margin: 6px 0 0 0; padding-left: 20px; line-height: 1.8;">
              <li v-for="(e, ei) in tc.expected_results" :key="ei">{{ e }}</li>
            </ol>
          </div>
        </div>
      </div>
      <!-- 旧接口：仅字符串列表 testPoints -->
      <div
        v-else-if="module.testPoints && module.testPoints.length > 0"
        style="margin-bottom: 20px; padding: 10px; background-color: #f5f7fa; border-radius: 4px;"
      >
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
  return props.modules.some(
    (m) =>
      (m.testCases && m.testCases.length > 0) ||
      (m.testPoints && m.testPoints.length > 0)
  )
})
</script>