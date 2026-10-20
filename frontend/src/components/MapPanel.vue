<template>
  <!-- 地图容器:Leaflet 会接管这个 div 的显示 -->
  <div ref="mapEl" class="map-container">
    <div v-if="loading" class="loading-tip">图层加载中…</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css' // Leaflet 的样式文件,缺了地图控件会错位
import parseGeoraster from 'georaster' // 解析 tif 文件为内存中的栅格对象
import GeoRasterLayer from 'georaster-layer-for-leaflet' // 把栅格对象变成 Leaflet 图层
import { pixelToColor } from '../config/colors'

// ============ 组件说明 ============
// MapPanel 负责:初始化地图 + 根据"当前年份"加载对应的 tif 图层
// 父组件(App.vue)通过 props 传入年份;年份一变,这里自动换图层

const props = defineProps({
  year: { type: Number, required: true }, // 当前要显示的年份
})

const mapEl = ref(null)      // 地图 div 的引用(模板里的 ref="mapEl")
const loading = ref(false)   // 图层加载中提示
let map = null               // Leaflet 地图对象(全局只有一个)
let currentLayer = null      // 当前的栅格图层(换年份时先移除旧的)

// ============ 初始化地图(只执行一次) ============
onMounted(() => {
  // 1. 创建地图,底图用 OpenStreetMap 瓦片(免费、无需 key)
  map = L.map(mapEl.value, { zoomControl: true })
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  // 2. 初始视图放在武汉上空(经纬度 + 缩放级别)
  map.setView([30.6, 114.4], 9)
  // 3. 加载当前年份图层
  loadLayer(props.year)
})

// ============ 年份变化时切换图层 ============
watch(() => props.year, (newYear) => {
  loadLayer(newYear)
})

// ============ 核心:加载并渲染 tif ============
async function loadLayer(year) {
  if (!map) return
  loading.value = true
  try {
    // 1. 移除旧图层(如果有)
    if (currentLayer) {
      map.removeLayer(currentLayer)
      currentLayer = null
    }
    // 2. 拉取 tif 文件并解析(COG 格式,支持按需分层读取)
    const georaster = await parseGeoraster(`/data/layers/${year}.tif`)
    // 3. 转成 Leaflet 图层:每个像元按"地类编码 → 配色"上色
    currentLayer = new GeoRasterLayer({
      georaster,
      pixelValuesToColorFn: pixelToColor, // 上色回调(见 colors.js)
      resolution: 256,                    // 渲染分辨率:每屏幕像素取样,足够清晰
      opacity: 0.9,
    })
    currentLayer.addTo(map)
    // 4. 把地图视野对准图层范围(第一次加载时定位到武汉)
    const bounds = currentLayer.getBounds()
    if (bounds.isValid()) map.fitBounds(bounds)
  } catch (err) {
    console.error('图层加载失败:', err)
    alert(`图层加载失败:${err.message}`)
  } finally {
    loading.value = false
  }
}

// 把地图对象暴露给父组件(后面框选统计要用到 map 做交互)
defineExpose({ getMap: () => map })
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
}
.loading-tip {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000; /* 盖在地图上面 */
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
}
</style>
