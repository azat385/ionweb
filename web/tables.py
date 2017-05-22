import django_tables2 as tables
from .models import Data, Tag, Tag_group


class DataTable(tables.Table):
    class Meta:
        model = Data
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}