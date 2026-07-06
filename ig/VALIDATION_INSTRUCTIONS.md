# v2.0.0 validation instructions

Run `python scripts/validate_ig_static.py`, then `cd ig && npx --yes fsh-sushi@3.20.0 --out fsh-generated .`, then `java -jar publisher.jar -ig ig.ini` in a network-enabled or package-cached environment.
