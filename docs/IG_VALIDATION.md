# FHIR IG validation

Static checks:

```bash
make validate-fsh-static
make validate-ig-static
```

SUSHI, when Node.js/package resolution is available:

```bash
make sushi-build
```

HL7 IG Publisher, when `publisher.jar` is available:

```bash
PUBLISHER_JAR=/path/to/publisher.jar make ig-publisher
```
