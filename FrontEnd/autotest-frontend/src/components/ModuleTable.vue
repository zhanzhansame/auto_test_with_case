<template>
  <el-card class="box-card" v-if="modules.length > 0" style="margin-bottom: 20px;">
    <template #header>
      <div class="card-header" style="font-weight: bold;">
        <span>2. 模块解析与测试点生成</span>
      </div>
    </template>
    <el-table :data="modules" border style="width: 100%">
      <el-table-column prop="level1_module" label="一级模块" />
      <el-table-column prop="level2_module" label="二级模块" />
      <el-table-column prop="level3_function" label="功能点" />
      <el-table-column label="操作" width="120" align="center">
        <template #default="scope">
          <el-button
            v-if="!scope.row.testPoints && !scope.row.testCases"
            size="small" type="primary" plain
            :loading="scope.row.loading"
            @click="$emit('on-generate', scope.row, scope.$index)"
          >
            生成用例
          </el-button>
          <el-tag v-else type="success">已生成</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
defineProps({
  modules: Array
})
defineEmits(['on-generate'])
</script>