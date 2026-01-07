import tkinter as tk
from tkinter import ttk, colorchooser
import math

class GeometryBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Python几何画板")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f8f8f8")
        
        # 状态变量
        self.current_tool = "select"
        self.current_color = "#2c3e50"
        self.current_thickness = 2
        self.shapes = []
        self.selected_shape = None
        self.is_drawing = False
        self.start_point = None
        self.temp_shape = None
        
        # 历史记录（用于撤销/重做）
        self.history = []
        self.history_index = -1
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建画布
        self.create_canvas()
        
        # 绑定事件
        self.bind_events()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建画布", command=self.new_canvas)
        file_menu.add_command(label="保存图形", command=self.save_canvas)
        file_menu.add_command(label="导出图片", command=self.export_canvas)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_command(label="删除选中", command=self.delete_selected)
        edit_menu.add_command(label="清空画布", command=self.clear_canvas)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 显示菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="显示/隐藏网格", command=self.toggle_grid)
        view_menu.add_command(label="显示/隐藏坐标", command=self.toggle_coords)
        menubar.add_cascade(label="显示", menu=view_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar_frame = tk.Frame(self.root, bg="#e9f5ff", height=60)
        toolbar_frame.pack(fill=tk.X, side=tk.TOP, pady=5, padx=5)
        
        # 工具按钮
        tools = [
            ("select", "选择", "#00BCD4"),
            ("point", "点", "#e91e63"),
            ("segment", "线段", "#4CAF50"),
            ("ray", "射线", "#8BC34A"),
            ("line", "直线", "#FF5722"),
            ("circle", "圆", "#9C27B0"),
            ("rect", "矩形", "#2196F3"),
            ("triangle", "三角形", "#FF9800"),
            ("pen", "画笔", "#795548")
        ]
        
        for tool, text, color in tools:
            btn = tk.Button(toolbar_frame, text=text, width=8, height=2,
                          bg=color, fg="white", relief=tk.RAISED,
                          command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 颜色选择
        color_frame = tk.Frame(toolbar_frame, bg="#e9f5ff")
        color_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(color_frame, text="颜色:", bg="#e9f5ff").pack(side=tk.LEFT)
        self.color_btn = tk.Button(color_frame, width=3, height=1,
                                 bg=self.current_color, relief=tk.RAISED,
                                 command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT, padx=5)
        
        # 线宽选择
        thickness_frame = tk.Frame(toolbar_frame, bg="#e9f5ff")
        thickness_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(thickness_frame, text="线宽:", bg="#e9f5ff").pack(side=tk.LEFT)
        self.thickness_var = tk.IntVar(value=self.current_thickness)
        thickness_spin = tk.Spinbox(thickness_frame, from_=1, to=10,
                                  textvariable=self.thickness_var,
                                  width=5, command=self.update_thickness)
        thickness_spin.pack(side=tk.LEFT)
    
    def create_canvas(self):
        canvas_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.SUNKEN)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # 键盘快捷键
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
    
    def set_tool(self, tool):
        self.current_tool = tool
    
    def choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_btn.config(bg=color)
    
    def update_thickness(self):
        self.current_thickness = self.thickness_var.get()
    
    def on_mouse_down(self, event):
        self.start_point = (event.x, event.y)
        self.is_drawing = True
        
        if self.current_tool == "select":
            self.select_shape(event.x, event.y)
        elif self.current_tool == "point":
            self.draw_point(event.x, event.y)
    
    def on_mouse_drag(self, event):
        if not self.is_drawing:
            return
        
        # 删除临时图形
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
        
        # 绘制临时图形
        if self.current_tool in ["segment", "ray", "line", "circle", "rect", "triangle"]:
            self.temp_shape = self.draw_temp_shape(event.x, event.y)
    
    def on_mouse_up(self, event):
        if not self.is_drawing:
            return
        
        self.is_drawing = False
        
        # 删除临时图形
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
        
        # 绘制最终图形
        if self.current_tool in ["segment", "ray", "line", "circle", "rect", "triangle"]:
            self.draw_final_shape(event.x, event.y)
    
    def on_mouse_move(self, event):
        pass
    
    def select_shape(self, x, y):
        # 查找选中的图形
        self.selected_shape = None
        for shape in reversed(self.shapes):
            if shape.contains_point(x, y):
                self.selected_shape = shape
                shape.highlight()
                break
    
    def draw_point(self, x, y):
        shape = Point(x, y, self.current_color, self.current_thickness, self.canvas)
        self.add_shape(shape)
    
    def draw_temp_shape(self, x, y):
        if not self.start_point:
            return
        
        x1, y1 = self.start_point
        
        if self.current_tool == "segment":
            return self.canvas.create_line(x1, y1, x, y, 
                                        fill=self.current_color, 
                                        width=self.current_thickness, 
                                        dash=(5, 5))
        elif self.current_tool == "ray":
            # 射线：从起点到终点，再延伸一段
            dx, dy = x - x1, y - y1
            length = math.hypot(dx, dy)
            if length == 0:
                dx, dy = 1, 0
                length = 1
            x2, y2 = x1 + dx * 2, y1 + dy * 2
            return self.canvas.create_line(x1, y1, x2, y2, 
                                        fill=self.current_color, 
                                        width=self.current_thickness, 
                                        dash=(5, 5))
        elif self.current_tool == "line":
            # 直线：穿过两个点，延伸到画布边缘
            return self.canvas.create_line(x1, y1, x, y, 
                                        fill=self.current_color, 
                                        width=self.current_thickness, 
                                        dash=(5, 5))
        elif self.current_tool == "circle":
            r = math.hypot(x - x1, y - y1)
            return self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, 
                                        outline=self.current_color, 
                                        width=self.current_thickness, 
                                        dash=(5, 5))
        elif self.current_tool == "rect":
            return self.canvas.create_rectangle(x1, y1, x, y, 
                                              outline=self.current_color, 
                                              width=self.current_thickness, 
                                              dash=(5, 5))
    
    def draw_final_shape(self, x, y):
        if not self.start_point:
            return
        
        x1, y1 = self.start_point
        
        if self.current_tool == "segment":
            shape = Segment(x1, y1, x, y, self.current_color, self.current_thickness, self.canvas)
        elif self.current_tool == "ray":
            shape = Ray(x1, y1, x, y, self.current_color, self.current_thickness, self.canvas)
        elif self.current_tool == "line":
            shape = Line(x1, y1, x, y, self.current_color, self.current_thickness, self.canvas)
        elif self.current_tool == "circle":
            r = math.hypot(x - x1, y - y1)
            shape = Circle(x1, y1, r, self.current_color, self.current_thickness, self.canvas)
        elif self.current_tool == "rect":
            shape = Rectangle(x1, y1, x, y, self.current_color, self.current_thickness, self.canvas)
        elif self.current_tool == "triangle":
            shape = Triangle(x1, y1, x, y, x1, y, self.current_color, self.current_thickness, self.canvas)
        else:
            return
        
        self.add_shape(shape)
    
    def add_shape(self, shape):
        self.shapes.append(shape)
        self.update_history()
    
    def update_history(self):
        # 清除当前索引后的历史记录
        self.history = self.history[:self.history_index + 1]
        # 添加新的历史记录
        self.history.append([shape.clone() for shape in self.shapes])
        self.history_index = len(self.history) - 1
    
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.restore_history()
    
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore_history()
    
    def restore_history(self):
        if 0 <= self.history_index < len(self.history):
            # 清除当前所有图形
            for shape in self.shapes:
                shape.delete()
            self.shapes = []
            
            # 恢复历史记录
            for shape_data in self.history[self.history_index]:
                shape = shape_data.clone()
                shape.redraw(self.canvas)
                self.shapes.append(shape)
    
    def delete_selected(self):
        if self.selected_shape:
            self.selected_shape.delete()
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
            self.update_history()
    
    def clear_canvas(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes = []
        self.selected_shape = None
        self.update_history()
    
    def new_canvas(self):
        self.clear_canvas()
    
    def save_canvas(self):
        # 保存功能（可以实现为保存图形数据或导出为图片）
        print("保存功能尚未实现")
    
    def export_canvas(self):
        # 导出功能
        print("导出功能尚未实现")
    
    def toggle_grid(self):
        print("网格功能尚未实现")
    
    def toggle_coords(self):
        print("坐标功能尚未实现")

# 几何图形基类
class Shape:
    def __init__(self, color, thickness):
        self.color = color
        self.thickness = thickness
        self.canvas = None
        self.id = None
    
    def contains_point(self, x, y):
        pass
    
    def highlight(self):
        if self.id:
            self.canvas.itemconfig(self.id, width=self.thickness + 2)
    
    def delete(self):
        if self.id:
            self.canvas.delete(self.id)
            self.id = None
    
    def clone(self):
        pass
    
    def redraw(self, canvas):
        self.canvas = canvas

# 点类
class Point(Shape):
    def __init__(self, x, y, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x = x
        self.y = y
        self.canvas = canvas
        self.radius = max(3, thickness)
        self.id = self.canvas.create_oval(x - self.radius, y - self.radius,
                                         x + self.radius, y + self.radius,
                                         fill=color)
    
    def contains_point(self, x, y):
        return math.hypot(x - self.x, y - self.y) <= self.radius + 5
    
    def clone(self):
        return Point(self.x, self.y, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        self.id = self.canvas.create_oval(self.x - self.radius, self.y - self.radius,
                                         self.x + self.radius, self.y + self.radius,
                                         fill=self.color)

# 线段类
class Segment(Shape):
    def __init__(self, x1, y1, x2, y2, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.canvas = canvas
        self.id = self.canvas.create_line(x1, y1, x2, y2, 
                                         fill=color, width=thickness)
    
    def contains_point(self, x, y):
        # 计算点到线段的距离
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.hypot(dx, dy)
        
        if length == 0:
            return math.hypot(x - self.x1, y - self.y1) <= self.thickness + 5
        
        t = ((x - self.x1) * dx + (y - self.y1) * dy) / (length * length)
        t = max(0, min(1, t))
        
        px = self.x1 + t * dx
        py = self.y1 + t * dy
        
        return math.hypot(x - px, y - py) <= self.thickness + 5
    
    def clone(self):
        return Segment(self.x1, self.y1, self.x2, self.y2, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        self.id = self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, 
                                         fill=self.color, width=self.thickness)

# 射线类
class Ray(Shape):
    def __init__(self, x1, y1, x2, y2, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.canvas = canvas
        
        # 计算射线终点（延伸）
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            dx, dy = 1, 0
            length = 1
        
        scale = 10  # 延伸10倍
        self.id = self.canvas.create_line(x1, y1, x1 + dx * scale, y1 + dy * scale,
                                         fill=color, width=thickness)
    
    def contains_point(self, x, y):
        # 简化实现：检查点是否在射线附近
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.hypot(dx, dy)
        
        if length == 0:
            return False
        
        # 检查点是否在射线方向上
        t = ((x - self.x1) * dx + (y - self.y1) * dy) / (length * length)
        if t < 0:
            return False
        
        px = self.x1 + t * dx
        py = self.y1 + t * dy
        
        return math.hypot(x - px, y - py) <= self.thickness + 5
    
    def clone(self):
        return Ray(self.x1, self.y1, self.x2, self.y2, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        dx, dy = self.x2 - self.x1, self.y2 - self.y1
        length = math.hypot(dx, dy)
        if length == 0:
            dx, dy = 1, 0
            length = 1
        scale = 10
        self.id = self.canvas.create_line(self.x1, self.y1, self.x1 + dx * scale, self.y1 + dy * scale,
                                         fill=self.color, width=self.thickness)

# 直线类
class Line(Shape):
    def __init__(self, x1, y1, x2, y2, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.canvas = canvas
        
        # 计算直线与画布边缘的交点
        xmin, ymin, xmax, ymax = 0, 0, canvas.winfo_width(), canvas.winfo_height()
        
        # 计算直线的参数方程
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0:  # 垂直线
            self.id = canvas.create_line(x1, ymin, x1, ymax, 
                                        fill=color, width=thickness)
        else:
            m = dy / dx
            b = y1 - m * x1
            
            # 计算与左右边缘的交点
            y_left = m * xmin + b
            y_right = m * xmax + b
            
            # 计算与上下边缘的交点
            x_top = (ymin - b) / m if m != 0 else xmin
            x_bottom = (ymax - b) / m if m != 0 else xmin
            
            # 确定可见部分的端点
            points = []
            if 0 <= y_left <= ymax:
                points.append((xmin, y_left))
            if 0 <= y_right <= ymax:
                points.append((xmax, y_right))
            if 0 <= x_top <= xmax:
                points.append((x_top, ymin))
            if 0 <= x_bottom <= xmax:
                points.append((x_bottom, ymax))
            
            # 取两个最远的点
            if len(points) >= 2:
                points.sort(key=lambda p: (p[0] - x1)**2 + (p[1] - y1)**2)
                self.id = canvas.create_line(points[0], points[-1], 
                                           fill=color, width=thickness)
    
    def contains_point(self, x, y):
        # 检查点是否在直线附近
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.hypot(dx, dy)
        
        if length == 0:
            return False
        
        # 计算点到直线的距离
        distance = abs(dy * x - dx * y + self.x2 * self.y1 - self.y2 * self.x1) / length
        
        return distance <= self.thickness + 5
    
    def clone(self):
        return Line(self.x1, self.y1, self.x2, self.y2, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        
        if dx == 0:  # 垂直线
            self.id = canvas.create_line(self.x1, 0, self.x1, canvas.winfo_height(), 
                                        fill=self.color, width=self.thickness)
        else:
            m = dy / dx
            b = self.y1 - m * self.x1
            
            # 计算与画布边缘的交点
            xmin, ymin, xmax, ymax = 0, 0, canvas.winfo_width(), canvas.winfo_height()
            y_left = m * xmin + b
            y_right = m * xmax + b
            
            points = []
            if 0 <= y_left <= ymax:
                points.append((xmin, y_left))
            if 0 <= y_right <= ymax:
                points.append((xmax, y_right))
            
            if len(points) >= 2:
                self.id = canvas.create_line(points[0], points[-1], 
                                           fill=self.color, width=self.thickness)

# 圆类
class Circle(Shape):
    def __init__(self, x, y, radius, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x = x
        self.y = y
        self.radius = radius
        self.canvas = canvas
        self.id = self.canvas.create_oval(x - radius, y - radius, 
                                         x + radius, y + radius,
                                         outline=color, width=thickness)
    
    def contains_point(self, x, y):
        # 检查点是否在圆上或圆内（考虑线宽）
        distance = math.hypot(x - self.x, y - self.y)
        return abs(distance - self.radius) <= self.thickness + 5
    
    def clone(self):
        return Circle(self.x, self.y, self.radius, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        self.id = self.canvas.create_oval(self.x - self.radius, self.y - self.radius, 
                                         self.x + self.radius, self.y + self.radius,
                                         outline=self.color, width=self.thickness)

# 矩形类
class Rectangle(Shape):
    def __init__(self, x1, y1, x2, y2, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.canvas = canvas
        self.id = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                              outline=color, width=thickness)
    
    def contains_point(self, x, y):
        # 检查点是否在矩形的边上
        if (abs(x - self.x1) <= self.thickness + 5 or abs(x - self.x2) <= self.thickness + 5) and 
           (self.y1 - 5 <= y <= self.y2 + 5):
            return True
        if (abs(y - self.y1) <= self.thickness + 5 or abs(y - self.y2) <= self.thickness + 5) and 
           (self.x1 - 5 <= x <= self.x2 + 5):
            return True
        return False
    
    def clone(self):
        return Rectangle(self.x1, self.y1, self.x2, self.y2, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        self.id = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                              outline=self.color, width=self.thickness)

# 三角形类
class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3, color, thickness, canvas):
        super().__init__(color, thickness)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.canvas = canvas
        self.id = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, 
                                           outline=color, width=thickness, 
                                           fill="")
    
    def contains_point(self, x, y):
        # 检查点是否在三角形的边上
        return (self._point_on_segment(x, y, self.x1, self.y1, self.x2, self.y2) or
                self._point_on_segment(x, y, self.x2, self.y2, self.x3, self.y3) or
                self._point_on_segment(x, y, self.x3, self.y3, self.x1, self.y1))
    
    def _point_on_segment(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        
        if length == 0:
            return math.hypot(px - x1, py - y1) <= self.thickness + 5
        
        t = ((px - x1) * dx + (py - y1) * dy) / (length * length)
        t = max(0, min(1, t))
        
        cx = x1 + t * dx
        cy = y1 + t * dy
        
        return math.hypot(px - cx, py - cy) <= self.thickness + 5
    
    def clone(self):
        return Triangle(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, self.color, self.thickness, None)
    
    def redraw(self, canvas):
        super().redraw(canvas)
        self.id = self.canvas.create_polygon(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, 
                                           outline=self.color, width=self.thickness, 
                                           fill="")

# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryBoard(root)
    root.mainloop()