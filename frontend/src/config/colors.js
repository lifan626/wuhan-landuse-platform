// ============ 地类配色表(全端唯一配置源) ============
// 图例面板、地图图层、图表都从这里取颜色,保证全站颜色语义一致
// 配色遵循土地利用制图通用惯例:耕地金黄、林地深绿、草地浅绿、水体蓝、
// 建设用地红、未利用地灰、湿地青

export const CLASS_COLORS = {
  1: { name: '耕地', color: '#FAD966' },
  2: { name: '林地', color: '#217836' },
  3: { name: '草地', color: '#9ECC59' },
  4: { name: '水体', color: '#2673BF' },
  5: { name: '建设用地', color: '#D93838' },
  6: { name: '未利用地', color: '#A6A6A6' },
  7: { name: '湿地', color: '#33A6A6' },
}

// 供 georaster 图层上色的回调:像元值 → 颜色(0=无效值 → 透明)
export function pixelToColor(values) {
  const code = values[0]
  if (!code || !CLASS_COLORS[code]) return null // null = 透明(不渲染)
  return CLASS_COLORS[code].color
}
