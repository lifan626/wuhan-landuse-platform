<template>
  <!-- 图例面板:展示各地类的颜色与名称 -->
  <div class="legend">
    <div class="legend-title">图例</div>
    <div v-for="(info, code) in CLASS_COLORS" :key="code" class="legend-row">
      <span class="legend-color" :style="{ background: info.color }"></span>
      <span class="legend-name">{{ info.name }}</span>
    </div>
  </div>
</template>

<script setup>
import { CLASS_COLORS } from '../config/colors'

// ============ 组件说明 ============
// 图例直接从配色表生成——配色表是唯一来源,
// 所以图例和地图图层永远一致(不会出现图例说蓝、图层画红的情况)
</script>

<style scoped>
.legend {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 6px;
  padding: 10px 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  width: 150px;
}
.legend-title {
  font-weight: bold;
  margin-bottom: 6px;
  font-size: 14px;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 3px 0;
  font-size: 13px;
}
.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
}
</style>
