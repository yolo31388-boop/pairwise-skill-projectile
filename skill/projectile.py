"""技能弹道与命中系统 - 含9个bug"""
from dataclasses import dataclass, field

@dataclass
class Projectile:
    pid: str
    skill_id: str
    x: float
    y: float
    vx: float
    vy: float
    speed: float = 5.0  # bug1: 固定速度
    radius: float = 1.0
    pierce: int = 0  # bug4: 无穿透限制
    bounce: int = 0  # bug5: 随机反弹
    life: float = 999.0  # bug7: 无生命周期
    faction: str = "all"  # bug8: 无阵营

class ProjectileSystem:
    def __init__(self):
        self.projectiles: list[Projectile] = []
        self.targets: list[dict] = []

    def get_speed(self, skill_id: str) -> float:
        # bug1: 固定速度
        return 5.0

    def check_collision(self, proj: Projectile, target: dict) -> bool:
        # bug2: 只看中心点
        dx = proj.x - target["x"]
        dy = proj.y - target["y"]
        return dx == 0 and dy == 0

    def check_hit_on_path(self, proj: Projectile, target: dict, dt: float) -> bool:
        # bug3: 瞬时判定不插值
        return self.check_collision(proj, target)

    def get_pierce_limit(self, skill_id: str) -> int:
        # bug4: 无限制
        return 999

    def calculate_bounce_angle(self, angle: float, normal: float) -> float:
        # bug5: 随机反弹
        import random
        return random.uniform(0, 360)

    def get_aoe_radius(self, skill_id: str) -> float:
        # bug6: 固定范围
        return 5.0

    def get_max_lifetime(self, skill_id: str) -> float:
        # bug7: 无生命周期
        return 999.0

    def can_hit_target(self, proj: Projectile, target_faction: str) -> bool:
        # bug8: 能命中友军
        return True

    def calculate_multi_hit_damage(self, hits: int, base_damage: float) -> float:
        # bug9: 多弹道只算一次
        return base_damage
