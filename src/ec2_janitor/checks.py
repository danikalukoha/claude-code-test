from dataclasses import dataclass, field


@dataclass
class InstanceReport:
    instance_id: str
    state: str
    missing_tags: list[str] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.missing_tags)


def _tag_map(instance: dict) -> dict[str, str]:
    return {t["Key"]: t["Value"] for t in instance.get("Tags", [])}


def audit_instance(instance: dict, required_tags: list[str]) -> InstanceReport:
    instance_id = instance["InstanceId"]
    state = instance["State"]["Name"]
    tags = _tag_map(instance)
    missing = [tag for tag in required_tags if tag not in tags]
    return InstanceReport(instance_id=instance_id, state=state, missing_tags=missing)


def audit_instances(instances: list[dict], required_tags: list[str]) -> list[InstanceReport]:
    return [audit_instance(i, required_tags) for i in instances]
