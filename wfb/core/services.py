from typing import List
from django.db.models import Model, QuerySet

#  internals
from .utils import get_client_ip
from .models import HitCount, UrlHit
from .models import Skill


class CoreService(object):
    @classmethod
    def create_skills(cls, model_obj: Model, skills: List[str]):
        for skillname in skills:
            # trim spaces
            skillname = skillname.strip()
            if skillname:
                skill, created = Skill.objects.get_or_create(name=skillname)
                model_obj.skills.add(skill)

    @classmethod
    def search(cls, qs: QuerySet, query: str, *args, **kwargs) -> QuerySet:
        pass


def hit_count_service(request):
    """
    To track the views count of the specific url.
    If a user logs out and logs in again and view the page again, it will be counted
    """
    if not request.session.session_key:
        request.session.save()
    s_key = request.session.session_key
    ip = get_client_ip(request)
    url, url_created = UrlHit.objects.get_or_create(url=request.path)

    if url_created:
        track, created = HitCount.objects.get_or_create(
            url_hit=url, ip=ip, session=s_key
        )
        if created:
            url.increase()
            request.session[ip] = ip
            request.session[request.path] = request.path
    else:
        if ip and request.path not in request.session:
            track, created = HitCount.objects.get_or_create(
                url_hit=url, ip=ip, session=s_key
            )
            if created:
                url.increase()
                request.session[ip] = ip
                request.session[request.path] = request.path
    return url.hits_count
