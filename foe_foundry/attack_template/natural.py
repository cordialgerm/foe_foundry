from .template import AttackTemplate

## Natural Weapons

# Claw
# Bite
# Stomp
# Tail
# Tentacle
# Slam


class _Claw(AttackTemplate):
    def __init__(self):
        super().__init__(name="Claw")


class _Bite(AttackTemplate):
    pass


class _Stomp(AttackTemplate):
    pass


class _Tail(AttackTemplate):
    pass


class _Tentacle(AttackTemplate):
    pass


class _Slam(AttackTemplate):
    pass


Claw: AttackTemplate = _Claw()
Bite: AttackTemplate = _Bite()
Stomp: AttackTemplate = _Stomp()
Tail: AttackTemplate = _Tail()
Tentacle: AttackTemplate = _Tentacle()
Slam: AttackTemplate = _Slam()
