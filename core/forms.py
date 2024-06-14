from django import forms
from django.forms.widgets import Select, TextInput
from django.utils.safestring import mark_safe

from core.models import Course, CourseAudience, CourseLecture, CourseRequirement


class DatalistTextInput(TextInput):
    def __init__(self, attrs=None, datalist=[]):
        if attrs is not None:
            attrs["datalist"] = "__".join(datalist)

        super().__init__(attrs)
        if "list" not in self.attrs or "datalist" not in self.attrs:
            raise ValueError(
                'DatalistTextInput widget is missing required attrs "list" or "datalist"'
            )

        self.datalist_name = self.attrs["list"]

        self.datalist = datalist

    def render(self, **kwargs):
        part1 = super().render(**kwargs)
        opts = " ".join([f"<option>{x}</option>" for x in self.datalist])
        part2 = f'<datalist id="{self.datalist_name}">{opts}</datalist>'
        return part1 + mark_safe(part2)


class SearchSelectInput(Select):
    def __init__(
        self, attrs=None, options: list[dict[str, str]] = None, *args, **kwargs
    ):
        super().__init__(*args, attrs, **kwargs)


class TestDatalist(forms.Form):
    foo = forms.CharField(
        max_length=10,
        widget=DatalistTextInput(
            attrs={
                "list": "foolist",
                "class": "input input-bordered",
            },
            datalist=["foo", "bar", "baz", "quux"],
        ),
    )


# class BaseModelForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             class_str = None
#             print(visible.widget_type)
#             match visible.widget_type:
#                 case "text" | "number":
#                     class_str = "input input-bordered"
#                 case "checkbox":
#                     class_str = "checkbox"
#                 case "select" | "selectmultiple":
#                     class_str = "select select-bordered"
#                 case "clearablefile":
#                     class_str = "file-input file-input-bordered"
#                 case _:
#                     class_str = "input input-bordered"
#
#             visible.field.widget.attrs["class"] = class_str


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ["user", "enrolled_users"]
        widgets = {
            "preview": forms.FileInput(
                attrs={"accept": "video/mp4,video/webm,video/ogg,video/mpeg"}
            )
        }


class CourseRequirementForm(forms.ModelForm):
    class Meta:
        model = CourseRequirement
        fields = ["description"]


class CourseAudienceForm(forms.ModelForm):
    class Meta:
        model = CourseAudience
        fields = ["description"]


class CourseLectureForm(forms.ModelForm):
    class Meta:
        model = CourseLecture
        exclude = ["id", "created_at", "updated_at", "order"]
