from decimal import *

class TransformationPipeline(object):
    def convert_to_decmial(self, item, field_name):
        val = item[field_name]
        if val is not None and val != "-":
            val = val.replace("US $", "")
            val = Decimal(val)
        else:
            val = 0
        item[field_name] = val

    def process_item(self, item, spider):
        self.convert_to_decmial(item, "new_current_min")
        self.convert_to_decmial(item, "new_current_avg")
        self.convert_to_decmial(item, "used_current_min")
        self.convert_to_decmial(item, "used_current_avg")
        item['year'] = int(item['year']);
        return item
