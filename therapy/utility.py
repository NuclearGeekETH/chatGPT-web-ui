import os
import json

DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(DATA_FOLDER, "data.json")

def load_history():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return "Patient history saved!"

def get_patient_history_text():
    data = load_history()
    return json.dumps(data, indent=2, ensure_ascii=False)

def flatten_text_list(lst):
    return "\n".join(lst if lst else [])

def unflatten_text_list(val):
    return [line.strip() for line in val.splitlines() if line.strip()]

def flatten_table(lst, fields):
    return [[d.get(f, "") for f in fields] for d in lst]

def unflatten_table(rows, fields):
    import pandas as pd
    out = []
    # If rows is a pandas DataFrame, convert to a list of lists:
    if isinstance(rows, pd.DataFrame):
        rows = rows.values.tolist()
    for row in rows:
        if isinstance(row, (list, tuple)) and len(row) == len(fields) and any(str(x).strip() for x in row):
            out.append({f: row[i] for i, f in enumerate(fields)})
    return out

def flatten_basic_info(data):
    b = data["basic_info"]
    return [
        b.get("full_name", ""),
        b.get("preferred_name", ""),
        b.get("pronouns", ""),
        b.get("date_of_birth", ""),
        b["contact_info"].get("email", ""),
        b["contact_info"].get("phone", ""),
        b["contact_info"].get("address", ""),
        b["emergency_contact"].get("name", ""),
        b["emergency_contact"].get("relationship", ""),
        b["emergency_contact"].get("phone", "")
    ]

def unflatten_basic_info(values, data):
    b = data["basic_info"]
    b["full_name"] = values[0]
    b["preferred_name"] = values[1]
    b["pronouns"] = values[2]
    b["date_of_birth"] = values[3]
    b["contact_info"]["email"] = values[4]
    b["contact_info"]["phone"] = values[5]
    b["contact_info"]["address"] = values[6]
    b["emergency_contact"]["name"] = values[7]
    b["emergency_contact"]["relationship"] = values[8]
    b["emergency_contact"]["phone"] = values[9]
    return data

def flatten_cultural_identity(data):
    cul = data["cultural_identity"]
    return [
        cul.get("ethnicity", ""),
        cul.get("religion", ""),
        cul.get("gender_identity", ""),
        cul.get("sexual_orientation", ""),
        cul.get("other_important_factors", "")
    ]

def unflatten_cultural_identity(values, data):
    cul = data["cultural_identity"]
    cul["ethnicity"] = values[0]
    cul["religion"] = values[1]
    cul["gender_identity"] = values[2]
    cul["sexual_orientation"] = values[3]
    cul["other_important_factors"] = values[4]
    return data

def flatten_preferences(data):
    pr = data["preferences"]
    tp = pr["therapist_preferences"]
    return [
        flatten_text_list(pr.get("preferred_therapy_styles", [])),
        flatten_text_list(pr.get("what_helps", [])),
        flatten_text_list(pr.get("what_doesnt_help", [])),
        tp.get("gender", ""),
        tp.get("age", ""),
        tp.get("cultural_background", ""),
        tp.get("languages", "")
    ]

def unflatten_preferences(values, data):
    pr = data["preferences"]
    tp = pr["therapist_preferences"]
    pr["preferred_therapy_styles"] = unflatten_text_list(values[0])
    pr["what_helps"] = unflatten_text_list(values[1])
    pr["what_doesnt_help"] = unflatten_text_list(values[2])
    tp["gender"] = values[3]
    tp["age"] = values[4]
    tp["cultural_background"] = values[5]
    tp["languages"] = values[6]
    return data

def flatten_social_history(data):
    soc = data["social_history"]
    return [
        soc.get("living_situation", ""),
        soc.get("relationship_status", ""),
        soc.get("children", ""),
        flatten_text_list(soc.get("close_support_systems", []))
    ]

def unflatten_social_history(values, data):
    soc = data["social_history"]
    soc["living_situation"] = values[0]
    soc["relationship_status"] = values[1]
    soc["children"] = values[2]
    soc["close_support_systems"] = unflatten_text_list(values[3])
    return data

def form_load():
    data = load_history()
    out = []
    out += flatten_basic_info(data)
    out.append(flatten_text_list(data.get("presenting_issues", [])))
    out.append(flatten_text_list(data.get("goals_for_therapy", [])))
    out.append(flatten_table(data["mental_health_history"]["diagnoses"], ["diagnosis","diagnosed_by","date_diagnosed","current_status","notes"]))
    out.append(flatten_table(data["mental_health_history"]["symptoms"], ["symptom","onset","severity","frequency","triggers","coping_strategies"]))
    out.append(flatten_table(data["mental_health_history"]["medications"], ["name","dosage","prescriber","start_date","end_date","side_effects","effectiveness"]))
    out.append(flatten_table(data["mental_health_history"]["past_treatments"],["type","provider","duration","outcome","reason_stopped"]))
    out.append(flatten_table(data["mental_health_history"]["hospitalizations"],["reason","facility","date","duration","outcome"]))
    out.append(flatten_text_list(data["medical_history"].get("chronic_conditions", [])))
    out.append(flatten_table(data["medical_history"]["current_medications"], ["name","dosage","condition"]))
    out.append(flatten_text_list(data["medical_history"].get("significant_past_illnesses_injuries", [])))
    out.append(flatten_table(data["substance_use"]["current_or_past_use"], ["substance","use_pattern","duration","amount","last_use","concerns"]))
    out.append(flatten_table(data["family_history"]["mental_illness"], ["relation","diagnosis","details"]))
    out.append(flatten_table(data["family_history"]["medical_conditions"], ["relation","condition","details"]))
    out.append(flatten_table(data["family_history"]["relationship_dynamics"], ["relation","dynamic","impact_on_you"]))
    out.append(flatten_table(data["trauma_history"], ["type","age_at_time","impact","support_received","current_effects"]))
    out += flatten_social_history(data)
    out.append(flatten_table(data["social_history"]["work_education_history"], ["role","institution","duration","satisfaction"]))
    out.append(flatten_text_list(data["social_history"].get("legal_issues", [])))
    out.append(flatten_table(data.get("strengths_interests", []), ["strength_or_interest","notes"]))
    out.append(flatten_text_list(data.get("values_beliefs", [])))
    out += flatten_cultural_identity(data)
    out += flatten_preferences(data)
    out.append(flatten_text_list(data.get("questions_concerns_for_therapist", [])))
    out.append(data.get("other_notes", ""))
    out.append(data)
    return out

def form_save(*args):
    idx = 0
    data = args[-1]  # Last arg is full dict
    # Basic Info (10)
    bi = list(args[idx:idx+10])
    data = unflatten_basic_info(bi, data)
    idx += 10
    data["presenting_issues"] = unflatten_text_list(args[idx]); idx += 1
    data["goals_for_therapy"] = unflatten_text_list(args[idx]); idx += 1
    mh = data["mental_health_history"]
    mh["diagnoses"] = unflatten_table(args[idx], ["diagnosis","diagnosed_by","date_diagnosed","current_status","notes"]); idx += 1
    mh["symptoms"] = unflatten_table(args[idx], ["symptom","onset","severity","frequency","triggers","coping_strategies"]); idx += 1
    mh["medications"] = unflatten_table(args[idx], ["name","dosage","prescriber","start_date","end_date","side_effects","effectiveness"]); idx += 1
    mh["past_treatments"] = unflatten_table(args[idx], ["type","provider","duration","outcome","reason_stopped"]); idx += 1
    mh["hospitalizations"] = unflatten_table(args[idx], ["reason","facility","date","duration","outcome"]); idx += 1
    medhist = data["medical_history"]
    medhist["chronic_conditions"] = unflatten_text_list(args[idx]); idx += 1
    medhist["current_medications"] = unflatten_table(args[idx], ["name","dosage","condition"]); idx += 1
    medhist["significant_past_illnesses_injuries"] = unflatten_text_list(args[idx]); idx += 1
    sub = data["substance_use"]
    sub["current_or_past_use"] = unflatten_table(args[idx], ["substance","use_pattern","duration","amount","last_use","concerns"]); idx += 1
    fam = data["family_history"]
    fam["mental_illness"] = unflatten_table(args[idx], ["relation","diagnosis","details"]); idx += 1
    fam["medical_conditions"] = unflatten_table(args[idx], ["relation","condition","details"]); idx += 1
    fam["relationship_dynamics"] = unflatten_table(args[idx], ["relation","dynamic","impact_on_you"]); idx += 1
    data["trauma_history"] = unflatten_table(args[idx], ["type","age_at_time","impact","support_received","current_effects"]); idx += 1
    soc_vals = list(args[idx:idx+4])
    data = unflatten_social_history(soc_vals, data)
    idx += 4
    data["social_history"]["work_education_history"] = unflatten_table(args[idx], ["role","institution","duration","satisfaction"]); idx += 1
    data["social_history"]["legal_issues"] = unflatten_text_list(args[idx]); idx += 1
    data["strengths_interests"] = unflatten_table(args[idx], ["strength_or_interest","notes"]); idx += 1
    data["values_beliefs"] = unflatten_text_list(args[idx]); idx += 1
    cul_vals = list(args[idx:idx+5])
    data = unflatten_cultural_identity(cul_vals, data)
    idx += 5
    pref_vals = list(args[idx:idx+7])
    data = unflatten_preferences(pref_vals, data)
    idx += 7
    data["questions_concerns_for_therapist"] = unflatten_text_list(args[idx]); idx += 1
    data["other_notes"] = args[idx]; idx += 1
    save_history(data)
    return "History saved!"