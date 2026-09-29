"""技能弹道与命中系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill.projectile import ProjectileSystem, Projectile

class TestSpeedBySkill:
    def test_arrow_faster_than_fireball(self):
        ps = ProjectileSystem()
        s1 = ps.get_speed("arrow")
        s2 = ps.get_speed("fireball")
        assert s1 != s2

class TestCollisionRadius:
    def test_grazing_hit_counts(self):
        ps = ProjectileSystem()
        proj = Projectile("p1", "arrow", 0, 0, 1, 0, radius=2)
        target = {"x": 1.5, "y": 0, "radius": 1}
        assert ps.check_collision(proj, target) == True

class TestPathInterpolation:
    def test_projectile_passing_through_triggers_hit(self):
        ps = ProjectileSystem()
        proj = Projectile("p1", "arrow", 0, 0, 10, 0)
        target = {"x": 5, "y": 0, "radius": 1}
        assert ps.check_hit_on_path(proj, target, 1.0) == True

class TestPierceLimit:
    def test_pierce_has_limit(self):
        ps = ProjectileSystem()
        limit = ps.get_pierce_limit("pierce_arrow")
        assert limit < 10

class TestBouncePhysics:
    def test_bounce_angle_is_reflection(self):
        ps = ProjectileSystem()
        # 入射角45度，法线90度，反射角应该是135度
        angle = ps.calculate_bounce_angle(45, 90)
        assert 120 <= angle <= 150

class TestAOERadius:
    def test_different_skills_different_aoe(self):
        ps = ProjectileSystem()
        r1 = ps.get_aoe_radius("small_bomb")
        r2 = ps.get_aoe_radius("meteor")
        assert r2 > r1

class TestLifetime:
    def test_projectile_has_finite_lifetime(self):
        ps = ProjectileSystem()
        life = ps.get_max_lifetime("arrow")
        assert life < 999

class TestFactionHit:
    def test_cannot_hit_ally(self):
        ps = ProjectileSystem()
        proj = Projectile("p1", "heal", 0, 0, 0, 0, faction="ally")
        assert ps.can_hit_target(proj, "ally") == False
        assert ps.can_hit_target(proj, "enemy") == True

class TestMultiHitDamage:
    def test_multiple_projectiles_stack_damage(self):
        ps = ProjectileSystem()
        dmg = ps.calculate_multi_hit_damage(3, 100)
        assert dmg == 300
