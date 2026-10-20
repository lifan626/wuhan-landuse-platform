<template>
  <!-- 整体布局:顶部年份栏 + 中间地图 + 右下角图例 -->
  <div class="app">
    <TimelineBar v-model="currentYear" :years="YEARS" />
    <div class="main-area">
      <MapPanel :year="currentYear" />
      <div class="legend-wrap">
        <LegendPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MapPanel from './components/MapPanel.vue'
import TimelineBar from './components/TimelineBar.vue'
import LegendPanel from './components/LegendPanel.vue'

// ============ 组件说明 ============
// App.vue 是根组件:持有"当前年份"这个全局状态,把它传给子组件
// 年份一变 → MapPanel 自动切换图层;时间轴播放 → 年份连续变化 → 形成动画
// YEARS 目前写死(开发期);后面改为从后端 /api/layers 接口获取

const YEARS = [2003, 2005, 2010, 2013] // 平台的代表年份
const currentYear = ref(2003)          // 初始显示 2003 年
</script>

<style>
/* 全局样式:让页面占满整个窗口 */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.main-area {
  position: relative;
  flex: 1; /* 占据除年份栏外的全部剩余空间 */
}
.legend-wrap {
  position: absolute;
  right: 12px;
  bottom: 24px;
  z-index: 1000; /* 图例盖在地图上面 */
}
</style>
