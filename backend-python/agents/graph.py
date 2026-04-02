from agents.diagnostic_agent import run_diagnostic
from agents.postmortem_agent import run_postmortem
from agents.remediation_agent import run_remediation
from agents.triage_agent import run_triage


async def run_alert_workflow(alert: dict) -> dict:
    triage = await run_triage(alert)
    diagnostic = await run_diagnostic(alert, triage)
    remediation = await run_remediation(alert, diagnostic)
    postmortem = await run_postmortem(alert, diagnostic, remediation)
    return {
        "triage": triage,
        "diagnostic": diagnostic,
        "remediation": remediation,
        "postmortem": postmortem,
    }
