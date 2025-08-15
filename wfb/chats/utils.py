

def generate_room_name(job_id: str, proposal_id: str) -> str:
    return f"J{job_id}_P{proposal_id}"


def decode_room_name(room_name: str):
    jobx, proposalx = room_name.split("_")
    job_id = jobx[1:]
    proposal_id = proposalx[1:]
    return job_id, proposal_id
