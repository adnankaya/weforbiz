from django.db.models import QuerySet, Q
from wfb.core.services import CoreService

from .exceptions import TotalPointsNotEnoughException

class ProfessionalService(CoreService):
    @classmethod
    def update_points(cls, professional, job):
        if professional.total_points > job.required_points:
            professional.total_points -= job.required_points
            professional.save()
            return professional
        raise TotalPointsNotEnoughException(
            _("Professional total points are not enough!")
        )

    @classmethod
    def search(cls, qs: QuerySet, query: str, *args, **kwargs) -> QuerySet:
        """
        TODO : will add full text search
        # TODO when full name entered ???
        """
        res = qs.filter(
            Q(title__icontains=query)
            | Q(bio__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )

        return res