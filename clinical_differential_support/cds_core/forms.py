from django import forms

from .models import ClinicalItem, ReviewRecord, Source


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.replace(",", "\n").splitlines() if line.strip()]


class ReviewDecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=ReviewRecord.Decision.choices,
        label="審核決定 (Review decision)",
    )
    notes = forms.CharField(
        label="審核備註 (Review notes)",
        min_length=12,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="記錄內容、來源與規則審核理由。Record the content, source, and rule review rationale.",
    )


class ClinicalItemDraftForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[
            (ClinicalItem.Status.DRAFT, "Draft"),
            (ClinicalItem.Status.IN_REVIEW, "In review"),
        ],
        label="草稿狀態 (Draft status)",
    )
    missing_questions_text = forms.CharField(
        label="下一步詢問 (Ask next)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="每行一項或用逗號分隔。One item per line or comma-separated.",
    )
    supporting_findings_text = forms.CharField(
        label="支持 finding (Supporting findings)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="每行一項或用逗號分隔。One item per line or comma-separated.",
    )
    opposing_findings_text = forms.CharField(
        label="反向 finding (Opposing findings)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="每行一項或用逗號分隔。One item per line or comma-separated.",
    )

    class Meta:
        model = ClinicalItem
        fields = [
            "chief_complaint",
            "item_type",
            "title",
            "title_zh",
            "title_en",
            "summary",
            "summary_zh",
            "summary_en",
            "urgency",
            "status",
            "review_due_at",
            "missing_questions_text",
            "supporting_findings_text",
            "opposing_findings_text",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "summary_zh": forms.Textarea(attrs={"rows": 3}),
            "summary_en": forms.Textarea(attrs={"rows": 3}),
            "review_due_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["missing_questions_text"].initial = "\n".join(
                self.instance.missing_questions
            )
            self.fields["supporting_findings_text"].initial = "\n".join(
                self.instance.supporting_findings
            )
            self.fields["opposing_findings_text"].initial = "\n".join(
                self.instance.opposing_findings
            )

    def save(self, commit=True):
        item = super().save(commit=False)
        item.missing_questions = _split_lines(
            self.cleaned_data.get("missing_questions_text", "")
        )
        item.supporting_findings = _split_lines(
            self.cleaned_data.get("supporting_findings_text", "")
        )
        item.opposing_findings = _split_lines(
            self.cleaned_data.get("opposing_findings_text", "")
        )
        if commit:
            item.save()
            self.save_m2m()
        return item


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = [
            "publisher",
            "title",
            "url",
            "publication_date",
            "access_date",
            "version_label",
        ]
        labels = {
            "publisher": "發布者 (Publisher)",
            "title": "來源標題 (Source title)",
            "url": "來源網址 (Source URL)",
            "publication_date": "發布日期 (Publication date)",
            "access_date": "存取日期 (Access date)",
            "version_label": "版本標籤 (Version label)",
        }
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date"}),
            "access_date": forms.DateInput(attrs={"type": "date"}),
        }


class ClinicalItemSourceLinkForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Source.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="來源連結 (Source links)",
        help_text="選擇此臨床項目的支持來源。Select the evidence sources linked to this clinical item.",
    )

    def __init__(self, *args, item: ClinicalItem | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.fields["sources"].queryset = Source.objects.all()
        if item is not None:
            self.fields["sources"].initial = item.sources.values_list("pk", flat=True)

    def save(self) -> list[Source]:
        if self.item is None:
            raise ValueError("ClinicalItemSourceLinkForm requires an item before save().")
        selected_sources = list(self.cleaned_data["sources"])
        self.item.sources.set(selected_sources)
        return selected_sources


class HeadacheIntakeForm(forms.Form):
    age = forms.IntegerField(label="年齡 (Age)", min_value=0, max_value=120, required=False)
    onset_peak_minutes = forms.IntegerField(
        label="多久達到最劇烈，分鐘 (Time to peak, minutes)",
        min_value=0,
        required=False,
    )
    headache_days_per_month = forms.IntegerField(
        label="每月頭痛天數 (Headache days/month)",
        min_value=0,
        max_value=31,
        required=False,
    )
    acute_medication_days_per_month = forms.IntegerField(
        label="每月急性止痛藥使用天數 (Acute medication days/month)",
        min_value=0,
        max_value=31,
        required=False,
    )

    severe_intensity = forms.BooleanField(label="嚴重強度 (Severe intensity)", required=False)
    fever = forms.BooleanField(label="發燒 (Fever)", required=False)
    meningism = forms.BooleanField(label="腦膜刺激徵象 (Meningism)", required=False)
    neurologic_deficit = forms.BooleanField(label="神經學缺損 (Neurologic deficit)", required=False)
    altered_mental_status = forms.BooleanField(
        label="意識或精神狀態改變 (Altered mental status)",
        required=False,
    )
    recent_trauma = forms.BooleanField(label="近期外傷 (Recent trauma)", required=False)
    immunocompromised = forms.BooleanField(
        label="免疫功能低下 (Immunocompromised)",
        required=False,
    )
    malignancy_history = forms.BooleanField(
        label="惡性腫瘤病史 (Malignancy history)",
        required=False,
    )
    jaw_claudication = forms.BooleanField(label="下顎跛行 (Jaw claudication)", required=False)
    eye_pain_redness = forms.BooleanField(label="眼痛或紅眼 (Eye pain/redness)", required=False)
    unilateral_orbital_pain = forms.BooleanField(
        label="單側眼眶痛 (Unilateral orbital pain)",
        required=False,
    )
    autonomic_features = forms.BooleanField(
        label="自律神經症狀 (Autonomic features)",
        required=False,
    )
    photophobia = forms.BooleanField(label="畏光 (Photophobia)", required=False)
    nausea = forms.BooleanField(label="噁心 (Nausea)", required=False)
    recurrent_pattern = forms.BooleanField(label="反覆型態 (Recurrent pattern)", required=False)
    bilateral_pressure = forms.BooleanField(label="雙側壓迫感 (Bilateral pressure)", required=False)

    clinician_notes = forms.CharField(
        label="臨床備註 (Clinician notes)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="請勿輸入可識別病人資料。Do not enter patient identifiers in this MVP.",
    )


class AbdominalPainIntakeForm(forms.Form):
    age = forms.IntegerField(label="年齡 (Age)", min_value=0, max_value=120, required=False)
    pain_duration_hours = forms.IntegerField(
        label="腹痛時間，小時 (Pain duration, hours)",
        min_value=0,
        required=False,
    )

    generalized_abdominal_pain = forms.BooleanField(
        label="非定位或廣泛性腹痛 (Generalized or nonlocalized abdominal pain)",
        required=False,
    )
    severe_abdominal_pain = forms.BooleanField(
        label="劇烈腹痛 (Severe abdominal pain)",
        required=False,
    )
    rebound_guarding = forms.BooleanField(
        label="反彈痛或肌肉防衛 (Rebound tenderness or guarding)",
        required=False,
    )
    rigid_abdomen = forms.BooleanField(
        label="板狀腹或明顯腹壁僵硬 (Rigid abdomen)",
        required=False,
    )
    hemodynamic_instability = forms.BooleanField(
        label="血流動力不穩定 (Hemodynamic instability)",
        required=False,
    )
    fever = forms.BooleanField(label="發燒 (Fever)", required=False)
    right_lower_quadrant_pain = forms.BooleanField(
        label="右下腹痛 (Right lower quadrant pain)",
        required=False,
    )
    leukocytosis = forms.BooleanField(
        label="白血球升高 (Leukocytosis)",
        required=False,
    )
    migration_to_rlq = forms.BooleanField(
        label="疼痛轉移到右下腹 (Migration to right lower quadrant)",
        required=False,
    )
    right_upper_quadrant_pain = forms.BooleanField(
        label="右上腹痛 (Right upper quadrant pain)",
        required=False,
    )
    postprandial_ruq_pain = forms.BooleanField(
        label="飯後右上腹痛 (Postprandial right upper quadrant pain)",
        required=False,
    )
    jaundice = forms.BooleanField(label="黃疸 (Jaundice)", required=False)
    vomiting = forms.BooleanField(label="嘔吐 (Vomiting)", required=False)
    abdominal_distension = forms.BooleanField(
        label="腹脹 (Abdominal distension)",
        required=False,
    )
    no_flatus = forms.BooleanField(
        label="無排氣 (No flatus)",
        required=False,
    )
    recent_abdominal_surgery = forms.BooleanField(
        label="近期腹部手術 (Recent abdominal surgery)",
        required=False,
    )
    neutropenia = forms.BooleanField(
        label="嗜中性白血球低下 (Neutropenia)",
        required=False,
    )
    immunocompromised = forms.BooleanField(
        label="免疫功能低下 (Immunocompromised)",
        required=False,
    )
    pregnancy_possible = forms.BooleanField(
        label="可能懷孕 (Pregnancy possible)",
        required=False,
    )
    positive_pregnancy_test = forms.BooleanField(
        label="驗孕陽性 (Positive pregnancy test)",
        required=False,
    )
    vaginal_bleeding = forms.BooleanField(
        label="陰道出血 (Vaginal bleeding)",
        required=False,
    )
    syncope = forms.BooleanField(
        label="暈厥或近暈厥 (Syncope or near-syncope)",
        required=False,
    )
    clinically_stable = forms.BooleanField(
        label="目前臨床穩定 (Clinically stable)",
        required=False,
    )

    clinician_notes = forms.CharField(
        label="臨床備註 (Clinician notes)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="請勿輸入病人可識別資料。Do not enter patient identifiers in this MVP.",
    )


class DyspneaIntakeForm(forms.Form):
    age = forms.IntegerField(label="年齡 (Age)", min_value=0, max_value=120, required=False)
    dyspnea_duration_hours = forms.IntegerField(
        label="呼吸困難時間，小時 (Dyspnea duration, hours)",
        min_value=0,
        required=False,
    )
    dyspnea_duration_weeks = forms.IntegerField(
        label="呼吸困難時間，週 (Dyspnea duration, weeks)",
        min_value=0,
        required=False,
    )

    acute_dyspnea = forms.BooleanField(
        label="急性呼吸困難 (Acute dyspnea)",
        required=False,
    )
    chronic_persistent_breathlessness = forms.BooleanField(
        label="慢性持續呼吸困難超過 8 週 (Chronic persistent breathlessness over 8 weeks)",
        required=False,
    )
    severe_dyspnea = forms.BooleanField(
        label="嚴重呼吸困難 (Severe dyspnea)",
        required=False,
    )
    hypoxemia = forms.BooleanField(
        label="低血氧或新出現 SpO2 下降 (Hypoxemia or new oxygen desaturation)",
        required=False,
    )
    cyanosis = forms.BooleanField(label="發紺 (Cyanosis)", required=False)
    inability_to_speak = forms.BooleanField(
        label="無法完整說句子 (Unable to speak in sentences)",
        required=False,
    )
    altered_mental_status = forms.BooleanField(
        label="意識改變、混亂或躁動 (Altered mental status, confusion, or agitation)",
        required=False,
    )
    hemodynamic_instability = forms.BooleanField(
        label="血流動力不穩定 (Hemodynamic instability)",
        required=False,
    )
    chest_pain = forms.BooleanField(label="胸痛 (Chest pain)", required=False)
    syncope = forms.BooleanField(label="暈厥或近暈厥 (Syncope or near-syncope)", required=False)
    hemoptysis = forms.BooleanField(label="咯血 (Hemoptysis)", required=False)
    unilateral_leg_swelling = forms.BooleanField(
        label="單側腿部腫脹 (Unilateral leg swelling)",
        required=False,
    )
    cough = forms.BooleanField(label="咳嗽 (Cough)", required=False)
    fever = forms.BooleanField(label="發燒 (Fever)", required=False)
    immunocompromised = forms.BooleanField(
        label="免疫功能低下 (Immunocompromised)",
        required=False,
    )
    wheeze = forms.BooleanField(label="喘鳴 (Wheeze)", required=False)
    known_asthma_copd = forms.BooleanField(
        label="已知氣喘或 COPD (Known asthma or COPD)",
        required=False,
    )
    orthopnea = forms.BooleanField(label="端坐呼吸 (Orthopnea)", required=False)
    paroxysmal_nocturnal_dyspnea = forms.BooleanField(
        label="陣發性夜間呼吸困難 (Paroxysmal nocturnal dyspnea)",
        required=False,
    )
    leg_edema = forms.BooleanField(label="下肢水腫 (Leg edema)", required=False)
    weight_gain = forms.BooleanField(label="近期體重增加 (Recent weight gain)", required=False)
    smoking_history = forms.BooleanField(label="吸菸史 (Smoking history)", required=False)
    clinically_stable = forms.BooleanField(
        label="目前臨床穩定 (Clinically stable)",
        required=False,
    )

    clinician_notes = forms.CharField(
        label="臨床備註 (Clinician notes)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="請勿輸入病人可識別資料。Do not enter patient identifiers in this MVP.",
    )


NO_PATIENT_ID_HELP = "請勿輸入病人識別資料。 / Do not enter patient identifiers in this MVP."


INTAKE_FORM_LABELS = {
    "HeadacheIntakeForm": {
        "age": "年齡 / Age",
        "onset_peak_minutes": "達到最痛時間（分鐘） / Time to peak, minutes",
        "headache_days_per_month": "每月頭痛天數 / Headache days/month",
        "acute_medication_days_per_month": "每月急性止痛藥使用天數 / Acute medication days/month",
        "severe_intensity": "嚴重疼痛 / Severe intensity",
        "fever": "發燒 / Fever",
        "meningism": "腦膜刺激徵象 / Meningism",
        "neurologic_deficit": "神經學缺損 / Neurologic deficit",
        "altered_mental_status": "意識或精神狀態改變 / Altered mental status",
        "recent_trauma": "近期頭部外傷 / Recent trauma",
        "immunocompromised": "免疫功能低下 / Immunocompromised",
        "malignancy_history": "惡性腫瘤病史 / Malignancy history",
        "jaw_claudication": "下顎跛行 / Jaw claudication",
        "eye_pain_redness": "眼痛或眼紅 / Eye pain/redness",
        "unilateral_orbital_pain": "單側眼眶疼痛 / Unilateral orbital pain",
        "autonomic_features": "自律神經症狀 / Autonomic features",
        "photophobia": "畏光 / Photophobia",
        "nausea": "噁心 / Nausea",
        "recurrent_pattern": "反覆發作型態 / Recurrent pattern",
        "bilateral_pressure": "雙側壓迫感 / Bilateral pressure",
        "clinician_notes": "臨床備註 / Clinician notes",
    },
    "ChestPainIntakeForm": {
        "age": "年齡 / Age",
        "symptom_duration_minutes": "症狀持續時間（分鐘） / Symptom duration, minutes",
        "ongoing_chest_pain": "持續胸痛 / Ongoing chest pain",
        "chest_pressure": "胸部壓迫或緊縮感 / Pressure or tightness",
        "radiation_left_arm_jaw": "放射到手臂、下顎或上腹 / Radiation to arm, jaw, or upper abdomen",
        "diaphoresis": "冒冷汗 / Diaphoresis",
        "severe_dyspnea": "嚴重呼吸困難 / Severe dyspnea",
        "syncope": "暈厥或近暈厥 / Syncope or near-syncope",
        "hemodynamic_instability": "血流動力不穩 / Hemodynamic instability",
        "tearing_radiating_back": "撕裂樣疼痛放射到背部 / Tearing pain radiating to back",
        "pleuritic_pain": "吸氣或胸膜性疼痛 / Pleuritic pain",
        "dyspnea": "呼吸困難 / Dyspnea",
        "unilateral_leg_swelling": "單側腿部腫脹 / Unilateral leg swelling",
        "stable_exertional_chest_pain": "穩定活動誘發胸痛 / Stable exertional chest pain",
        "relieved_by_rest": "休息可緩解 / Relieved by rest",
        "low_intermediate_acs_probability": "低至中等 ACS 可能性 / Low-to-intermediate ACS probability",
        "clinically_stable": "臨床穩定 / Clinically stable",
        "clinician_notes": "臨床備註 / Clinician notes",
    },
    "AbdominalPainIntakeForm": {
        "age": "年齡 / Age",
        "pain_duration_hours": "腹痛持續時間（小時） / Pain duration, hours",
        "generalized_abdominal_pain": "廣泛或無法定位腹痛 / Generalized or nonlocalized abdominal pain",
        "severe_abdominal_pain": "嚴重腹痛 / Severe abdominal pain",
        "rebound_guarding": "反彈痛或肌性防禦 / Rebound tenderness or guarding",
        "rigid_abdomen": "腹部僵硬 / Rigid abdomen",
        "hemodynamic_instability": "血流動力不穩 / Hemodynamic instability",
        "fever": "發燒 / Fever",
        "right_lower_quadrant_pain": "右下腹痛 / Right lower quadrant pain",
        "leukocytosis": "白血球增多 / Leukocytosis",
        "migration_to_rlq": "疼痛轉移到右下腹 / Migration to right lower quadrant",
        "right_upper_quadrant_pain": "右上腹痛 / Right upper quadrant pain",
        "postprandial_ruq_pain": "飯後右上腹痛 / Postprandial right upper quadrant pain",
        "jaundice": "黃疸 / Jaundice",
        "vomiting": "嘔吐 / Vomiting",
        "abdominal_distension": "腹脹 / Abdominal distension",
        "no_flatus": "未排氣 / No flatus",
        "recent_abdominal_surgery": "近期腹部手術 / Recent abdominal surgery",
        "neutropenia": "嗜中性球低下 / Neutropenia",
        "immunocompromised": "免疫功能低下 / Immunocompromised",
        "pregnancy_possible": "可能懷孕 / Pregnancy possible",
        "positive_pregnancy_test": "驗孕陽性 / Positive pregnancy test",
        "vaginal_bleeding": "陰道出血 / Vaginal bleeding",
        "syncope": "暈厥或近暈厥 / Syncope or near-syncope",
        "clinically_stable": "臨床穩定 / Clinically stable",
        "clinician_notes": "臨床備註 / Clinician notes",
    },
    "DyspneaIntakeForm": {
        "age": "年齡 / Age",
        "dyspnea_duration_hours": "呼吸困難持續時間（小時） / Dyspnea duration, hours",
        "dyspnea_duration_weeks": "呼吸困難持續時間（週） / Dyspnea duration, weeks",
        "acute_dyspnea": "急性呼吸困難 / Acute dyspnea",
        "chronic_persistent_breathlessness": "慢性持續呼吸困難超過 8 週 / Chronic persistent breathlessness over 8 weeks",
        "severe_dyspnea": "嚴重呼吸困難 / Severe dyspnea",
        "hypoxemia": "低血氧或新發氧飽和下降 / Hypoxemia or new oxygen desaturation",
        "cyanosis": "發紺 / Cyanosis",
        "inability_to_speak": "無法完整說句子 / Unable to speak in sentences",
        "altered_mental_status": "意識改變、混亂或躁動 / Altered mental status, confusion, or agitation",
        "hemodynamic_instability": "血流動力不穩 / Hemodynamic instability",
        "chest_pain": "胸痛 / Chest pain",
        "syncope": "暈厥或近暈厥 / Syncope or near-syncope",
        "hemoptysis": "咳血 / Hemoptysis",
        "unilateral_leg_swelling": "單側腿部腫脹 / Unilateral leg swelling",
        "cough": "咳嗽 / Cough",
        "fever": "發燒 / Fever",
        "immunocompromised": "免疫功能低下 / Immunocompromised",
        "wheeze": "喘鳴 / Wheeze",
        "known_asthma_copd": "已知氣喘或 COPD / Known asthma or COPD",
        "orthopnea": "端坐呼吸 / Orthopnea",
        "paroxysmal_nocturnal_dyspnea": "陣發性夜間呼吸困難 / Paroxysmal nocturnal dyspnea",
        "leg_edema": "下肢水腫 / Leg edema",
        "weight_gain": "近期體重增加 / Recent weight gain",
        "smoking_history": "吸菸史 / Smoking history",
        "clinically_stable": "臨床穩定 / Clinically stable",
        "clinician_notes": "臨床備註 / Clinician notes",
    },
}


def localize_intake_form_labels(form_class) -> None:
    for field_name, label in INTAKE_FORM_LABELS.get(form_class.__name__, {}).items():
        form_class.base_fields[field_name].label = label
    if "clinician_notes" in form_class.base_fields:
        form_class.base_fields["clinician_notes"].help_text = NO_PATIENT_ID_HELP


class ChestPainIntakeForm(forms.Form):
    age = forms.IntegerField(label="年齡 (Age)", min_value=0, max_value=120, required=False)
    symptom_duration_minutes = forms.IntegerField(
        label="症狀持續時間，分鐘 (Symptom duration, minutes)",
        min_value=0,
        required=False,
    )

    ongoing_chest_pain = forms.BooleanField(label="仍有胸痛 (Ongoing chest pain)", required=False)
    chest_pressure = forms.BooleanField(label="壓迫或緊縮感 (Pressure or tightness)", required=False)
    radiation_left_arm_jaw = forms.BooleanField(
        label="放射到左臂、下顎或上腹 (Radiation to arm, jaw, or upper abdomen)",
        required=False,
    )
    diaphoresis = forms.BooleanField(label="冒冷汗 (Diaphoresis)", required=False)
    severe_dyspnea = forms.BooleanField(label="嚴重呼吸困難 (Severe dyspnea)", required=False)
    syncope = forms.BooleanField(label="昏厥或近昏厥 (Syncope or near-syncope)", required=False)
    hemodynamic_instability = forms.BooleanField(
        label="血流動力不穩定 (Hemodynamic instability)",
        required=False,
    )
    tearing_radiating_back = forms.BooleanField(
        label="撕裂感並放射到背部 (Tearing pain radiating to back)",
        required=False,
    )
    pleuritic_pain = forms.BooleanField(label="吸氣或咳嗽加劇 (Pleuritic pain)", required=False)
    dyspnea = forms.BooleanField(label="呼吸困難 (Dyspnea)", required=False)
    unilateral_leg_swelling = forms.BooleanField(
        label="單側下肢腫脹 (Unilateral leg swelling)",
        required=False,
    )
    stable_exertional_chest_pain = forms.BooleanField(
        label="運動誘發且型態穩定 (Stable exertional chest pain)",
        required=False,
    )
    relieved_by_rest = forms.BooleanField(label="休息可緩解 (Relieved by rest)", required=False)
    low_intermediate_acs_probability = forms.BooleanField(
        label="低至中等 ACS 可能性 (Low-to-intermediate ACS probability)",
        required=False,
    )
    clinically_stable = forms.BooleanField(label="目前臨床穩定 (Clinically stable)", required=False)

    clinician_notes = forms.CharField(
        label="臨床備註 (Clinician notes)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="請勿輸入可識別病人資料。Do not enter patient identifiers in this MVP.",
    )
