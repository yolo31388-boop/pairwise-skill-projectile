"""技能弹道与命中系统"""
import math
from dataclasses import dataclass, field

# 按技能类型区分的弹道速度（箭矢快、火球慢、激光瞬发）
SKILL_SPEEDS = {
    "arrow": 12.0,
    "pierce_arrow": 12.0,
    "fireball": 6.0,
    "laser": 1000.0,
}
DEFAULT_SPEED = 8.0

# 穿透次数上限
PIERCE_LIMITS = {
    "arrow": 0,
    "pierce_arrow": 3,
    "fireball": 0,
    "laser": 5,
}
DEFAULT_PIERCE_LIMIT = 1

# AOE 范围按技能类型区分
AOE_RADII = {
    "small_bomb": 3.0,
    "fireball": 4.0,
    "meteor": 12.0,
}
DEFAULT_AOE_RADIUS = 2.0

# 最大生命周期（秒）
SKILL_LIFETIMES = {
    "arrow": 3.0,
    "pierce_arrow": 3.0,
    "fireball": 5.0,
    "laser": 0.5,
}
DEFAULT_LIFETIME = 4.0

# 最大反弹次数
MAX_BOUNCES = 3


@dataclass
class Projectile:
    pid: str
    skill_id: str
    x: float
    y: float
    vx: float
    vy: float
    speed: float = 5.0
    radius: float = 1.0
    pierce: int = 0
    bounce: int = 0
    life: float = 3.0
    faction: str = "enemy"


class ProjectileSystem:
    def __init__(self):
        self.projectiles: list[Projectile] = []
        self.targets: list[dict] = []

    def get_speed(self, skill_id: str) -> float:
        return SKILL_SPEEDS.get(skill_id, DEFAULT_SPEED)

    def check_collision(self, proj: Projectile, target: dict) -> bool:
        # 圆形碰撞体：中心距离 <= 双方半径之和即命中（擦边也算）
        target_radius = target.get("radius", 0.0)
        dx = proj.x - target["x"]
        dy = proj.y - target["y"]
        return dx * dx + dy * dy <= (proj.radius + target_radius) ** 2

    def check_hit_on_path(self, proj: Projectile, target: dict, dt: float) -> bool:
        # 沿弹道路径插值：线段到目标中心的最短距离 <= 半径之和即命中
        target_radius = target.get("radius", 0.0)
        hit_radius = proj.radius + target_radius
        px, py = proj.x, proj.y
        tx, ty = target["x"], target["y"]
        mx, my = proj.vx * dt, proj.vy * dt
        seg_len_sq = mx * mx + my * my
        if seg_len_sq == 0:
            return self.check_collision(proj, target)
        # 目标在路径线段上的投影参数 t ∈ [0, 1]
        t = ((tx - px) * mx + (ty - py) * my) / seg_len_sq
        t = max(0.0, min(1.0, t))
        closest_x = px + t * mx
        closest_y = py + t * my
        dx = tx - closest_x
        dy = ty - closest_y
        return dx * dx + dy * dy <= hit_radius * hit_radius

    def get_pierce_limit(self, skill_id: str) -> int:
        return PIERCE_LIMITS.get(skill_id, DEFAULT_PIERCE_LIMIT)

    def calculate_bounce_angle(self, angle: float, normal: float) -> float:
        # 物理反射：反射角 = 2 * 法线角 - 入射角
        return (2 * normal - angle) % 360

    def get_aoe_radius(self, skill_id: str) -> float:
        return AOE_RADII.get(skill_id, DEFAULT_AOE_RADIUS)

    def get_max_lifetime(self, skill_id: str) -> float:
        return SKILL_LIFETIMES.get(skill_id, DEFAULT_LIFETIME)

    def can_hit_target(self, proj: Projectile, target_faction: str) -> bool:
        # 阵营判定：不能命中同阵营目标
        return proj.faction != target_faction

    def calculate_multi_hit_damage(self, hits: int, base_damage: float) -> float:
        # 多弹道命中分别计算，伤害可叠加
        return hits * base_damage
