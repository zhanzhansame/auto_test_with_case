<template>
  <el-card class="box-card" v-if="hasPoints">
    <template #header>
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; font-weight: bold;">
        <span>3. 测试用例预览</span>
      </div>
    </template>
    <div v-for="(module, moduleIndex) in modules" :key="`module-${moduleIndex}`" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <div>
          <span style="font-weight: 600;">{{ module.level3_function || module.level2_module || module.level1_module }}</span>
          <span style="color: #606266; margin-left: 10px;">{{ module.level2_module ? `${module.level2_module} / ${module.level1_module}` : module.level1_module }}</span>
        </div>
        <el-button type="danger" text size="small" @click="$emit('on-delete-module', moduleIndex)">删除模块</el-button>
      </div>

      <div v-if="module.testCases && module.testCases.length > 0" style="padding: 10px; background-color: #f5f7fa; border-radius: 4px;">
        <div
          v-for="(tc, tcIndex) in module.testCases"
          :key="tc.case_id || tcIndex"
          style="margin-bottom: 16px; padding: 12px; background: #fff; border-radius: 4px; border: 1px solid #ebeef5;"
        >
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 12px;">
            <div>
              <div style="font-size: 14px; color: #303133; font-weight: 700; margin-bottom: 6px;">用例 {{ tc.case_id || tcIndex + 1 }}</div>
              <el-input
                v-model="tc.case_name"
                placeholder="用例名称"
                size="small"
                style="width: 360px;"
              />
            </div>
            <el-button type="danger" text size="small" @click="$emit('on-delete-case', moduleIndex, tcIndex)">删除用例</el-button>
          </div>

          <el-form label-position="top" label-width="0px" size="small">
            <el-form-item label="前置条件">
              <el-input
                v-model="tc.preconditions"
                placeholder="输入前置条件"
                clearable
              />
            </el-form-item>
            <el-form-item label="摘要">
              <el-input
                v-model="tc.summary"
                placeholder="输入摘要"
                clearable
              />
            </el-form-item>
            <el-form-item label="步骤（每行一条）">
              <el-input
                type="textarea"
                :rows="3"
                :model-value="tc.steps.join('\n')"
                @update:model-value="$emit('on-update-case', moduleIndex, tcIndex, 'steps', $event)"
                placeholder="请输入步骤，回车换行"
              />
            </el-form-item>
            <el-form-item label="预期结果（每行一条）">
              <el-input
                type="textarea"
                :rows="3"
                :model-value="tc.expected_results.join('\n')"
                @update:model-value="$emit('on-update-case', moduleIndex, tcIndex, 'expected_results', $event)"
                placeholder="请输入预期结果，回车换行"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div
        v-else-if="module.testPoints && module.testPoints.length > 0"
        style="padding: 10px; background-color: #f5f7fa; border-radius: 4px;"
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
const emit = defineEmits(['on-update-case', 'on-delete-case', 'on-delete-module'])
const hasPoints = computed(() => {
  return props.modules.some(
    (m) =>
      (m.testCases && m.testCases.length > 0) ||
      (m.testPoints && m.testPoints.length > 0)
  )
})
</script>