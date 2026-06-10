import math
import random
import matplotlib.pyplot as plt

def poisson_disk_sampling(width, height, r, k=30):
    """
    二维泊松圆盘采样算法 (Bridson's algorithm)
    
    参数:
        width, height: 采样区域的宽和高
        r: 样本之间的最小距离
        k: 拒绝前的最大尝试次数 (默认 k=30)
    返回:
        points: 生成的样本点列表 [(x, y), ...]
    """
    # 步骤 0: 初始化背景网格
    # 单元格大小设为 r / sqrt(2)，保证每个网格内最多只有一个点
    cell_size = r / math.sqrt(2)
    grid_width = math.ceil(width / cell_size)
    grid_height = math.ceil(height / cell_size)
    
    # 网格中存储点在 points 列表中的索引，-1 表示空
    grid = [[-1 for _ in range(grid_height)] for _ in range(grid_width)]
    
    points = []
    active_list = []

    def insert_point(p):
        """将新点存入列表、加入活动列表，并在网格中记录其索引"""
        points.append(p)
        idx = len(points) - 1
        active_list.append(idx)
        
        grid_x = int(p[0] / cell_size)
        grid_y = int(p[1] / cell_size)
        grid[grid_x][grid_y] = idx

    def is_valid_point(p):
        """检查点是否在域内，且与所有现有点的距离大于 r"""
        # 边界检查
        if not (0 <= p[0] < width and 0 <= p[1] < height):
            return False
            
        grid_x = int(p[0] / cell_size)
        grid_y = int(p[1] / cell_size)
        
        # 只需检查该单元格及其周围的 5x5 邻域
        start_x = max(0, grid_x - 2)
        end_x = min(grid_width - 1, grid_x + 2)
        start_y = max(0, grid_y - 2)
        end_y = min(grid_height - 1, grid_y + 2)
        
        for i in range(start_x, end_x + 1):
            for j in range(start_y, end_y + 1):
                neighbor_idx = grid[i][j]
                if neighbor_idx != -1:
                    neighbor = points[neighbor_idx]
                    # 计算距离的平方，避免开方运算
                    dist_sq = (neighbor[0] - p[0])**2 + (neighbor[1] - p[1])**2
                    if dist_sq < r**2:
                        return False
        return True

    # 步骤 1: 随机选择初始样本
    x0 = random.uniform(0, width)
    y0 = random.uniform(0, height)
    insert_point((x0, y0))

    # 步骤 2: 遍历活动列表
    while active_list:
        # 随机从活动列表中选取一个点
        rand_idx = random.randrange(len(active_list))
        curr_idx = active_list[rand_idx]
        curr_p = points[curr_idx]
        
        found = False
        # 尝试生成最多 k 个候选点
        for _ in range(k):
            # 随机角度
            angle = random.uniform(0, 2 * math.pi)
            # 在 [r, 2r] 圆环内均匀生成半径 (使用面积均匀采样法)
            radius = r * math.sqrt(random.uniform(1, 4))
            
            new_x = curr_p[0] + radius * math.cos(angle)
            new_y = curr_p[1] + radius * math.sin(angle)
            new_p = (new_x, new_y)
            
            # 如果候选点有效，将其发射为下一个样本点
            if is_valid_point(new_p):
                insert_point(new_p)
                found = True
                break
        
        # 如果 k 次尝试后均未找到合适的点，将其从活动列表中移除
        if not found:
            active_list.pop(rand_idx)
            
    return points

def visualize(points, width, height, r):
    """使用 matplotlib 可视化结果"""
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 绘制点阵
    ax.scatter(x, y, s=15, c='black', zorder=2)
    
    # 可选：绘制半径为 r/2 的圆圈（如果这些圆互不相交，则两点之间距离至少为 r）
    for px, py in points:
        circle = plt.Circle((px, py), r/2, color='blue', alpha=0.1, zorder=1)
        ax.add_patch(circle)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_title(f"Poisson Disk Sampling\nTotal Points: {len(points)}, Minimum Distance (r): {r}")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 参数设置：域范围为 100x100，最小样本距离 r=4
    WIDTH, HEIGHT = 100, 100
    RADIUS = 4
    K = 30
    
    print(f"Generating samples...")
    sample_points = poisson_disk_sampling(WIDTH, HEIGHT, RADIUS, K)
    print(f"Generated {len(sample_points)} points. Opening visualization...")
    
    visualize(sample_points, WIDTH, HEIGHT, RADIUS)