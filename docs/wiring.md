# Wiring

---

## Definitions

- `power` = 100-240V AC Converter Adapter to 5V DC
- `button` = push button
- `NPN` = NPN transistor BJT
- `MOSFET` = P-Channel logic level MOSFET

---

### Latching power circuit

- `button` first side -> `power`(-)
- `button` second side -> `MOSFET` Gate
- `button` second side -> any rpi gpio (choice it later)

- `MOSFET` Source -> `power`(+)
- `MOSFET` Drain -> rpi 5v pin
- `MOSFET` Gate -> 10k ohm risistor -> `power`(+) (pull-up)

- rpi GND -> `power`(-)
- rpi 5v pin -> 1k ohm risistor -> `NPN` Base
- `NPN` Emitter -> `power`(-)
- `NPN` Collector -> 1k ohm risistor -> `MOSFET` Gate

---
