import math
import random
import matplotlib.pyplot as plt

def poisson_disk_sampling_3d(width, height, depth, r, k=30):
    """
    三维泊松圆盘采样算法 (Bridson's algorithm)
    
    参数:
        width, height, depth: 采样区域的宽、高、深
        r: 样本之间的最小距离
        k: 拒绝前的最大尝试次数 (默认 k=30)
    返回:
        points: 生成的样本点列表 [(x, y, z), ...]
    """
    # 步骤 0: 初始化背景网格
    # 三维空间中，单元格大小设为 r / sqrt(3) 
    cell_size = r / math.sqrt(3)
    grid_width = math.ceil(width / cell_size)
    grid_height = math.ceil(height / cell_size)
    grid_depth = math.ceil(depth / cell_size)
    
    # 3D 网格中存储点在 points 列表中的索引，-1 表示空
    grid = [[[-1 for _ in range(grid_depth)] for _ in range(grid_height)] for _ in range(grid_width)]
    
    points = []
    active_list = []

    def insert_point(p):
        """将新点存入列表、加入活动列表，并在网格中记录其索引 [cite: 26]"""
        points.append(p)
        idx = len(points) - 1
        active_list.append(idx)
        
        grid_x = int(p[0] / cell_size)
        grid_y = int(p[1] / cell_size)
        grid_z = int(p[2] / cell_size)
        grid[grid_x][grid_y][grid_z] = idx

    def is_valid_point(p):
        """检查点是否在域内，且与所有现有点的距离大于 r """
        if not (0 <= p[0] < width and 0 <= p[1] < height and 0 <= p[2] < depth):
            return False
            
        grid_x = int(p[0] / cell_size)
        grid_y = int(p[1] / cell_size)
        grid_z = int(p[2] / cell_size)
        
        # 检查该单元格及其周围的 5x5x5 邻域
        start_x = max(0, grid_x - 2)
        end_x = min(grid_width - 1, grid_x + 2)
        start_y = max(0, grid_y - 2)
        end_y = min(grid_height - 1, grid_y + 2)
        start_z = max(0, grid_z - 2)
        end_z = min(grid_depth - 1, grid_z + 2)
        
        for i in range(start_x, end_x + 1):
            for j in range(start_y, end_y + 1):
                for l in range(start_z, end_z + 1):
                    neighbor_idx = grid[i][j][l]
                    if neighbor_idx != -1:
                        neighbor = points[neighbor_idx]
                        # 计算三维距离的平方
                        dist_sq = (neighbor[0] - p[0])**2 + (neighbor[1] - p[1])**2 + (neighbor[2] - p[2])**2
                        if dist_sq < r**2:
                            return False
        return True

    # 步骤 1: 随机选择初始样本 [cite: 25]
    x0 = random.uniform(0, width)
    y0 = random.uniform(0, height)
    z0 = random.uniform(0, depth)
    insert_point((x0, y0, z0))

    # 步骤 2: 遍历活动列表 [cite: 27]
    while active_list:
        rand_idx = random.randrange(len(active_list))
        curr_idx = active_list[rand_idx]
        curr_p = points[curr_idx]
        
        found = False
        # 尝试生成最多 k 个候选点 
        for _ in range(k):
            # 三维球体表面均匀随机采样方向
            theta = random.uniform(0, 2 * math.pi)
            z_dir = random.uniform(-1, 1)
            xy_len = math.sqrt(1 - z_dir**2)
            x_dir = xy_len * math.cos(theta)
            y_dir = xy_len * math.sin(theta)
            
            # 在 [r, 2r] 球壳内均匀生成半径 (考虑体积效应: r ∝ u^(1/3))
            # u 从 1 到 8 映射，使得半径从 r 到 2r
            radius = r * (random.uniform(1, 8)) ** (1/3)
            
            new_x = curr_p[0] + radius * x_dir
            new_y = curr_p[1] + radius * y_dir
            new_z = curr_p[2] + radius * z_dir
            new_p = (new_x, new_y, new_z)
            
            # 验证候选点 [cite: 28, 29]
            if is_valid_point(new_p):
                insert_point(new_p)
                found = True
                break
        
        # 失败则移除该点 [cite: 30]
        if not found:
            active_list.pop(rand_idx)
            
    return points

def visualize_3d(points, width, height, depth, r):
    """使用 matplotlib 绘制 3D 散点图"""
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    z = [p[2] for p in points]
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制三维点阵
    ax.scatter(x, y, z, s=10, c='black', alpha=0.8)
    
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_zlim(0, depth)
    ax.set_box_aspect([width, height, depth]) # 保持轴比例一致
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f"3D Poisson Disk Sampling\nTotal Points: {len(points)}, Minimum Distance (r): {r}")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 参数设置：域范围为 50x50x50，最小样本距离 r=4
    # 注意：3D 空间体积随边长呈立方增长，建议一开始不要将域设置过大，否则生成点数极多。
    WIDTH, HEIGHT, DEPTH = 50, 50, 50
    RADIUS = 4
    K = 30
    
    print(f"Generating 3D samples in {WIDTH}x{HEIGHT}x{DEPTH} volume...")
    sample_points = poisson_disk_sampling_3d(WIDTH, HEIGHT, DEPTH, RADIUS, K)
    print(f"Generated {len(sample_points)} points. Opening visualization...")
    
    visualize_3d(sample_points, WIDTH, HEIGHT, DEPTH, RADIUS)