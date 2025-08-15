from django import forms

from wfb.core.forms import SearchForm
from .models import Job, Proposal, Contract


class JobForm(forms.ModelForm):
    min_budget = forms.DecimalField(required=False)

    class Meta:
        model = Job
        fields = ("title", "description", "job_type", "min_budget", "max_budget")

    def clean_min_budget(self):
        min_budget = self.cleaned_data.get("min_budget") or 0
        return min_budget


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = (
            "amount",
            "coverletter",
            # "attachment", TODO
        )


class ContractForm(forms.ModelForm):
    job = forms.ModelChoiceField(queryset=Job.objects.all())
    proposal = forms.ModelChoiceField(queryset=Proposal.objects.all())

    class Meta:
        model = Contract
        fields = ("job", "proposal")


class AcceptContractForm(forms.Form):
    # TODO use UUIDField
    contract_id = forms.CharField(max_length=36)


class SubmitWorkForm(forms.Form):
    # TODO use UUIDField
    contract_id = forms.CharField(max_length=36)
    hours_worked = forms.IntegerField(required=False)


class AcceptWorkForm(forms.Form):
    # TODO use UUIDField
    contract_id = forms.CharField(max_length=36)
class FlagJobForm(forms.Form):
    reason = forms.CharField(max_length=280)


class JobSearchForm(SearchForm):
    pass

