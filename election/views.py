from datetime import datetime

from django.contrib import messages
from django.db import transaction
from django.db.models import Max, Sum
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import AnnouncedPuResults, Lga, PollingUnit

PARTIES = ["PDP", "DPP", "ACN", "PPA", "CDC", "JP", "ANPP", "LABO", "CPP"]


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


# ---------------------------------------------------------------
# QUESTION 1: Individual polling unit results
# ---------------------------------------------------------------
def polling_unit_result(request):
    polling_units = PollingUnit.objects.all().order_by("polling_unit_name", "uniqueid")

    selected_pu = None
    selected_lga = None
    results = []
    total_score = 0

    uid = request.GET.get("uniqueid", "").strip()
    if uid.isdigit():
        selected_pu = PollingUnit.objects.filter(uniqueid=int(uid)).first()
        if selected_pu:
            selected_lga = Lga.objects.filter(lga_id=selected_pu.lga_id).first()
            # polling_unit_uniqueid is a varchar column, so compare as string
            results = list(
                AnnouncedPuResults.objects
                .filter(polling_unit_uniqueid=str(selected_pu.uniqueid))
                .order_by("party_abbreviation")
            )
            total_score = sum(r.party_score for r in results)

    return render(request, "election/polling_unit_result.html", {
        "polling_units": polling_units,
        "selected_pu": selected_pu,
        "selected_lga": selected_lga,
        "results": results,
        "total_score": total_score,
        "searched": bool(uid),
    })


# ---------------------------------------------------------------
# QUESTION 2: Summed results for an LGA
# ---------------------------------------------------------------
def lga_summed_result(request):
    # Only show LGAs that actually have polling units
    lgas = (
        Lga.objects
        .filter(lga_id__in=PollingUnit.objects.values("lga_id"))
        .order_by("lga_name")
    )

    selected_lga = None
    totals = []
    grand_total = 0
    pu_count = 0

    lga_param = request.GET.get("lga", "").strip()
    if lga_param.isdigit():
        selected_lga = lgas.filter(lga_id=int(lga_param)).first()
        if selected_lga:
            # polling_unit.lga_id  ->  lga.lga_id
            pu_ids = [
                str(i) for i in
                PollingUnit.objects
                .filter(lga_id=selected_lga.lga_id)
                .values_list("uniqueid", flat=True)
            ]
            pu_count = len(pu_ids)

            rows = (
                AnnouncedPuResults.objects
                .filter(polling_unit_uniqueid__in=pu_ids)
                .values("party_abbreviation")
                .annotate(total=Sum("party_score"))
            )
            sums = {r["party_abbreviation"].strip(): r["total"] or 0 for r in rows}

            # Major parties first (even if 0), then any other parties found
            ordered = PARTIES + sorted(p for p in sums if p not in PARTIES)
            totals = [{"party": p, "total": sums.get(p, 0)} for p in ordered]
            grand_total = sum(t["total"] for t in totals)

    return render(request, "election/lga_summed_result.html", {
        "lgas": lgas,
        "selected_lga": selected_lga,
        "totals": totals,
        "grand_total": grand_total,
        "pu_count": pu_count,
        "searched": bool(lga_param),
    })


# ---------------------------------------------------------------
# QUESTION 3: Add a new polling unit + party scores
# ---------------------------------------------------------------
def add_polling_unit(request):
    lgas = (
        Lga.objects
        .filter(lga_id__in=PollingUnit.objects.values("lga_id"))
        .order_by("lga_name")
    )

    form = {
        "lga_id": "", "ward_id": "", "polling_unit_name": "",
        "polling_unit_number": "", "polling_unit_description": "",
        "lat": "", "longitude": "", "entered_by_user": "",
    }
    scores = {p: "" for p in PARTIES}
    errors = []

    if request.method == "POST":
        for key in form:
            form[key] = request.POST.get(key, "").strip()
        for p in PARTIES:
            scores[p] = request.POST.get(f"score_{p}", "").strip()

        # ---- validation ----
        if not form["lga_id"].isdigit():
            errors.append("Please select an LGA.")
        if not form["ward_id"].isdigit():
            errors.append("Ward ID is required and must be a number.")
        if not form["polling_unit_name"]:
            errors.append("Polling unit name is required.")
        if not form["entered_by_user"]:
            errors.append('"Entered by" is required.')

        parsed_scores = {}
        for p in PARTIES:
            val = scores[p]
            if val.isdigit():
                parsed_scores[p] = int(val)
            else:
                errors.append(f"Score for {p} must be a whole number (0 or more).")

        # ---- save ----
        if not errors:
            now = datetime.now()
            ip = get_client_ip(request)
            ward_id = int(form["ward_id"])

            next_pu_id = (
                PollingUnit.objects.filter(ward_id=ward_id)
                .aggregate(m=Max("polling_unit_id"))["m"] or 0
            ) + 1

            with transaction.atomic():
                pu = PollingUnit.objects.create(
                    polling_unit_id=next_pu_id,
                    ward_id=ward_id,
                    lga_id=int(form["lga_id"]),
                    polling_unit_number=form["polling_unit_number"] or None,
                    polling_unit_name=form["polling_unit_name"],
                    polling_unit_description=form["polling_unit_description"] or None,
                    lat=form["lat"] or None,
                    longitude=form["longitude"] or None,
                    entered_by_user=form["entered_by_user"],
                    date_entered=now,
                    user_ip_address=ip,
                )
                AnnouncedPuResults.objects.bulk_create([
                    AnnouncedPuResults(
                        polling_unit_uniqueid=str(pu.uniqueid),
                        party_abbreviation=party,
                        party_score=score,
                        entered_by_user=form["entered_by_user"],
                        date_entered=now,
                        user_ip_address=ip,
                    )
                    for party, score in parsed_scores.items()
                ])

            messages.success(
                request,
                f'Polling unit "{pu.polling_unit_name}" saved with results for all parties.'
            )
            return redirect(f"{reverse('election:polling_unit_result')}?uniqueid={pu.uniqueid}")

    party_rows = [{"abbr": p, "value": scores[p]} for p in PARTIES]

    return render(request, "election/add_polling_unit.html", {
        "lgas": lgas,
        "form": form,
        "party_rows": party_rows,
        "errors": errors,
    })
