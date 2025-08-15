from pydantic import BaseModel 

class Job(BaseModel):
    user_id: str
    job_name: str
    job_description: str
    repo_url: str

    def model_dump(self, mode="json"):
        return {
            "user_id": self.user_id,
            "job_name": self.job_name,
            "job_description": self.job_description,
            "repo_url": self.repo_url
        } if mode == "json" else super().model_dump(mode=mode)