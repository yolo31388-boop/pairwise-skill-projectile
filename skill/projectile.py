"""技能弹道与命中系统"""
import math
from dataclasses import dataclass, field

# 技能类型 -> 弹道速度（箭矢快、火球慢、激光瞬发）
SKILL_SPEEDS = {
    "arrow": 12.0,
    "pierce_arrow": 12.0,
    "fireball": 6.0,
    "laser": 1000.0,
    "heal": 8.0,
    "small_bomb": 5.0,
    "meteor": 4.0,
}
DEFAULT_SPEED = 8.0

# 技能类型 -> 穿透次数上限
PIERCE_LIMITS = {
    "pierce_arrow": 3,
    "arrow": 0,
    "fireball": 0,
    "laser": 5,
}
DEFAULT_PIERCE_LIMIT = 0

# 技能类型 -> AOE 半径（按技能类型区分，可随等级成长）
AOE_RADII = {
    "small_bomb": 3.0,
    "fireball": 4.0,
    "meteor": 10.0,
    "heal": 5.0,
}
DEFAULT_AOE_RADIUS = 3.0
AOE_LEVEL_GROWTH = 0.5

# 技能类型 -> 最大生命周期（秒）
LIFETIMES = {
    "arrow": 3.0,
    "pierce_arrow": 3.0,
    "fireball": 5.0,
    "laser": 0.5,
    "heal": 4.0,
    "small_bomb": 4.0,
    "meteor": 6.0,
}
DEFAULT_LIFETIME = 5.0

# 技能类型 -> 最大飞行距离
MAX_RANGES = {
    "arrow": 50.0,
    "fireball": 40.0,
    "laser": 100.0,
}
DEFAULT_MAX_RANGE = 60.0

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
    life: float = 999.0
    faction: str = "all"

class ProjectileSystem:
    def __init__(self):
        self.projectiles: list[Projectile] = []
        self.targets: list[dict] = []

    def get_speed(self, skill_id: str) -> float:
        return SKILL_SPEEDS.get(skill_id, DEFAULT_SPEED)

    def check_collision(self, proj: Projectile, target: dict) -> bool:
        # 圆形碰撞体：圆心距 <= 半径之和即命中（擦边也算）
        dx = proj.x - target["x"]
        dy = proj.y - target["y"]
        combined = proj.radius + target.get("radius", 0)
        return dx * dx + dy * dy <= combined * combined

    def check_hit_on_path(self, proj: Projectile, target: dict, dt: float) -> bool:
        # 按弹道路径插值：线段 (x,y)->(x+vx*dt, y+vy*dt) 与目标圆求交
        tx, ty = target["x"], target["y"]
        combined = proj.radius + target.get("radius", 0)
        dx = proj.vx * dt
        dy = proj.vy * dt
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            return self.check_collision(proj, target)
        # 目标圆心在线段上的投影参数 t ∈ [0,1]
        t = ((tx - proj.x) * dx + (ty - proj.y) * dy) / seg_len_sq
        t = max(0.0, min(1.0, t))
        closest_x = proj.x + t * dx
        closest_y = proj.y + t * dy
        ddx = closest_x - tx
        ddy = closest_y - ty
        return ddx * ddx + ddy * ddy <= combined * combined

    def get_pierce_limit(self, skill_id: str) -> int:
        return PIERCE_LIMITS.get(skill_id, DEFAULT_PIERCE_LIMIT)

    def calculate_bounce_angle(self, angle: float, normal: float) -> float:
        # 物理反射：反射角 = 2*法线角 - 入射角（入射角等于反射角）
        return (2.0 * normal - angle) % 360.0

    def get_aoe_radius(self, skill_id: str, level: int = 1) -> float:
        base = AOE_RADII.get(skill_id, DEFAULT_AOE_RADIUS)
        return base + AOE_LEVEL_GROWTH * max(0, level - 1)

    def get_max_lifetime(self, skill_id: str) -> float:
        return LIFETIMES.get(skill_id, DEFAULT_LIFETIME)

    def get_max_range(self, skill_id: str) -> float:
        return MAX_RANGES.get(skill_id, DEFAULT_MAX_RANGE)

    def can_hit_target(self, proj: Projectile, target_faction: str) -> bool:
        # 阵营判定：弹道只能命中对立阵营
        if proj.faction == "all":
            return True
        return proj.faction != target_faction

    def calculate_multi_hit_damage(self, hits: int, base_damage: float) -> float:
        # 多弹道命中分别计算，伤害叠加
        return hits * base_damage
