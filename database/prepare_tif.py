# -*- coding: utf-8 -*-
"""
展示轨预处理脚本:把原始土地利用栅格转成前端可直接渲染的 COG tif
==============================================================
【这个脚本干什么】
前端用 georaster 插件渲染 tif,要求文件满足三个条件:
  1. 坐标系是 WGS84(经纬度)——Leaflet 地图是经纬度的,栅格必须对齐
  2. COG 格式(内部有金字塔层级)——地图缩小视图时只读低层级,秒出
  3. 像元值是地类编码(1~7)——配色表按编码上色

【用法】
python prepare_tif.py 输入.tif 输出.tif [--clip minx,miny,maxx,maxy] [--remap clcd]

--clip :按经纬度范围裁剪(如 CLCD 是全国范围,裁剪出武汉)
--remap clcd :把 CLCD 的 9 类编码映射成平台的 7 类(见下方映射表)

【示例】
# 武汉本地数据(已裁切好、已是 1-7 编码),直接转换
python prepare_tif.py wh2003_refy.tif ..\\data\\layers\\2003.tif
"""
import sys
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject

# CLCD 9 类 → 平台 7 类 的映射表(CLCD 编码 → 平台编码)
# CLCD:1农田 2森林 3灌木 4草地 5水域 6冰雪 7裸地 8不透水面 9湿地
# 平台:1耕地 2林地 3草地 4水体 5建设用地 6未利用地 7湿地
CLCD_REMAP = {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 6, 7: 6, 8: 5, 9: 7}


def parse_args(argv):
    """解析命令行参数(返回 输入/输出/裁剪范围/是否CLCD映射)"""
    clip, remap = None, False
    i = 0
    while i < len(argv):
        if argv[i] == "--clip" and i + 1 < len(argv):
            clip = [float(v) for v in argv[i + 1].split(",")]  # 四个数:minx,miny,maxx,maxy
            i += 2
        elif argv[i] == "--remap" and i + 1 < len(argv) and argv[i + 1] == "clcd":
            remap = True
            i += 2
        else:
            i += 1
    src_path, dst_path = argv[0], argv[1]
    return src_path, dst_path, clip, remap


def make_cog(src_path, dst_path, clip=None, remap_clcd=False):
    """
    把任意投影/范围的分类栅格转成 WGS84 的 COG tif
    clip: [minx, miny, maxx, maxy] 经纬度范围(可选)
    """
    with rasterio.open(src_path) as src:
        # ---- 第一步:裁剪 + 重投影到 WGS84 ----
        # 计算目标网格:如果给了 clip,先算出输出窗口;否则处理整个范围
        if clip:
            # 把经纬度裁剪框转成源数据坐标系(源可能是 32649/Albers 等)
            from rasterio.warp import transform_bounds
            clip_src_crs = transform_bounds("EPSG:4326", src.crs, *clip)
            # 用源坐标系的范围创建窗口,window 比直接读全图快很多
            window = rasterio.windows.from_bounds(*clip_src_crs, transform=src.transform)
        else:
            window = None  # 不裁剪,读全图

        data = src.read(1, window=window)  # 读第一波段(分类栅格只有一个波段)
        # 无效值统一清为 0(不同数据源的 nodata 不同:武汉数据是 15、CLCD 是 0,统一口径后前端配色表只跳过 0)
        if src.nodata is not None and src.nodata != 0:
            data[data == src.nodata] = 0

        # 重投影参数:目标 = WGS84,分辨率为源数据的近似米制分辨率
        dst_transform, dst_w, dst_h = calculate_default_transform(
            src.crs, "EPSG:4326", src.width, src.height, *rasterio.windows.bounds(window, src.transform) if window else src.bounds
        )
        dst = np.empty((dst_h, dst_w), dtype=data.dtype)
        reproject(
            source=data,
            destination=dst,
            src_transform=src.window_transform(window) if window else src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs="EPSG:4326",
            resampling=Resampling.nearest,  # 分类数据必须最近邻,不能用双线性(会插出假编码)
        )

        # ---- 第二步:可选地类映射(CLCD 9 类 → 平台 7 类) ----
        if remap_clcd:
            mapped = np.zeros_like(dst)
            for clcd_code, plat_code in CLCD_REMAP.items():
                mapped[dst == clcd_code] = plat_code
            dst = mapped
        # 重投影时 nodata 可能被填成 0 之外的填充值,再次统一清 0
        dst[dst == 255] = 0

        # ---- 第三步:写出 COG(分块 + 内部金字塔,前端分层读取) ----
        profile = {
            "driver": "COG",          # 云优化 GeoTIFF 驱动,自动内嵌金字塔
            "width": dst_w,
            "height": dst_h,
            "count": 1,
            "dtype": dst.dtype,
            "crs": "EPSG:4326",
            "transform": dst_transform,
            "compress": "deflate",    # 无损压缩,分类栅格压缩率高(几百 KB~几 MB)
            "nodata": 0,              # 无效值统一为 0,配色表跳过 0
        }
        with rasterio.open(dst_path, "w", **profile) as dstf:
            dstf.write(dst, 1)
    print(f"完成: {dst_path}({dst_w}x{dst_h}, EPSG:4326, COG)")


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    make_cog(*args)
