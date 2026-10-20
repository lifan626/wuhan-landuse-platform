<template>
  <!-- 年份选择栏 + 时间轴播放控件 -->
  <div class="timeline">
    <!-- 每个年份一个按钮,当前年份高亮 -->
    <button
      v-for="y in years"
      :key="y"
      class="year-btn"
      :class="{ active: y === modelValue }"
      @click="$emit('update:modelValue', y)"
    >{{ y }}</button>
    <!-- 播放/暂停按钮:自动按时间顺序逐期切换 -->
    <button class="play-btn" @click="togglePlay">{{ playing ? '⏸ 暂停' : '▶ 播放' }}</button>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

// ============ 组件说明 ============
// TimelineBar 是年份选择与"土地利用变化动画"的控件
// 年份列表由父组件传入(将来从后端 /api/layers 获取)

const props = defineProps({
  years: { type: Array, required: true },   // 年份数组,如 [2003, 2005, 2010, 2013]
  modelValue: { type: Number, required: true }, // 当前选中年份(v-model)
})
const emit = defineEmits(['update:modelValue'])

const playing = ref(false) // 是否正在自动播放
let timer = null

// 播放:每 1.5 秒切到下一个年份,到末尾回到开头(循环)
function togglePlay() {
  if (playing.value) {
    clearInterval(timer)
    timer = null
    playing.value = false
    return
  }
  playing.value = true
  timer = setInterval(() => {
    const idx = props.years.indexOf(props.modelValue)
    const next = props.years[(idx + 1) % props.years.length] // 取模实现循环
    emit('update:modelValue', next)
  }, 1500)
}

// 组件卸载时清理定时器(防止内存泄漏/后台空转)
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.timeline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #fff;
  border-bottom: 1px solid #ddd;
}
.year-btn {
  padding: 6px 14px;
  border: 1px solid #ccc;
  background: #f8f8f8;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}
.year-btn.active {
  background: #2b6cb0;
  color: #fff;
  border-color: #2b6cb0;
}
.play-btn {
  margin-left: auto; /* 推到最右边 */
  padding: 6px 14px;
  background: #e53e3e;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
