def assess_rank_pattern(samples, selected_certificate_id, left=1, right=1):
    if type(left) is not int or type(right) is not int or not (0 <= left <= 2 and 0 <= right <= 2):
        raise ValueError("Exclude at most two indices at each end")
    selected = [s for s in samples if s["certificate_id"] == selected_certificate_id]
    if len(selected) != 1:
        raise ValueError("Select exactly one current certificate observation")
    selected = selected[0]
    family = [s for s in samples if s["recipe_id"] == selected["recipe_id"]]
    if any(s["rank_convention"] != selected["rank_convention"] for s in family):
        raise ValueError("Recompute the candidate with comparable rank conventions")
    if len({s["N"] for s in family}) != len(family):
        raise ValueError("Compare one selected trial per horizon for this recipe")
    eligible, unresolved, inconsistent = [], [], False
    for sample in family:
        n, profile = sample["N"], sample["rank_profile"]
        if type(n) is not int or n < 1 or len(profile) != n + 1:
            raise ValueError("Rank profile must contain V_0 through V_N")
        if any(type(r) is not int or r < 0 for r in profile):
            raise ValueError("Ranks must be nonnegative integers")
        retained = profile[left:n + 1 - right]
        if not (sample["certificate_checked"] is True and sample["grouping_checked"] is True):
            unresolved.append({"N": n, "reason": "unverified_certificate_or_grouping"})
        elif sample["rank_credible"] is not True:
            unresolved.append({"N": n, "reason": "ambiguous_rank"})
        elif len(retained) < 3:
            unresolved.append({"N": n, "reason": "insufficient_interior_indices"})
        elif len(set(retained)) != 1:
            inconsistent = True
            unresolved.append({"N": n, "reason": "nonconstant_interior_rank"})
        else:
            eligible.append((n, retained[0], sample["certificate_id"]))
    common_ranks = {r for _, r, _ in eligible}
    inconsistent = inconsistent or len(common_ranks) > 1
    selected_eligible = any(cid == selected_certificate_id for _, _, cid in eligible)
    confirmed = not inconsistent and len(eligible) >= 2 and selected_eligible
    return {
        "status": "confirmed" if confirmed else "inconsistent" if inconsistent else "insufficient_evidence",
        "boundary_exclusions": {"left": left, "right": right},
        "rank": next(iter(common_ranks)) if len(common_ranks) == 1 else None,
        "confirmed_horizons": sorted(n for n, _, _ in eligible) if confirmed else [],
        "selected_certificate_id": selected_certificate_id,
        "recipe_id": selected["recipe_id"],
        "rank_convention": selected["rank_convention"],
        "unresolved_samples": unresolved,
    }
