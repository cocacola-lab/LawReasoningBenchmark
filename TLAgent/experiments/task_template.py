import os
from utils import read_json

class Task1Template():
    def __init__(self, template_dir="input_template"):
        self.fact_template = read_json(os.path.join(template_dir, "fact_template.txt"))
        self.fact_final_template = read_json(os.path.join(template_dir, "fact_final_template.txt"))

    def get_template(self, template_name):
        template_name = template_name.lower()
        if "fact" in template_name:
            return self.fact_template.copy()
        elif "final" in template_name:
            return self.fact_final_template.copy()
        else:
            return None

    def get_agent_name(self, template_name):
        template_name = template_name.lower()
        if "fact" in template_name:
            return self.fact_template["agent_name"]
        elif "final" in template_name:
            return self.fact_final_template["agent_name"]
        else:
            return None

    def get_agent_description(self, template_name):
        template_name = template_name.lower()
        if "fact" in template_name:
            return self.fact_template["agent_description"]
        elif "final" in template_name:
            return self.fact_final_template["agent_description"]
        else:
            return None

    def get_agent_knowledge_base(self, template_name):
        template_name = template_name.lower()
        if "fact" in template_name:
            return self.fact_template["knowledge"]
        elif "final" in template_name:
            return self.fact_final_template["knowledge"]
        else:
            return None

    def get_agent_iteration_num(self, template_name):
        template_name = template_name.lower()
        if "fact" in template_name:
            return self.fact_template["max_iterations"]
        elif "final" in template_name:
            return self.fact_final_template["max_iterations"]
        else:
            return None

class Task2Template():
    def __init__(self, template_dir="input_template"):
        self.evid_template = read_json(os.path.join(template_dir, "evid_template.txt"))
        self.evid_link_template = read_json(os.path.join(template_dir, "evid_link_template.txt"))

    def get_template(self, template_name):
        template_name = template_name.lower()
        if "evid" in template_name:
            return self.evid_template.copy()
        elif "link" in template_name:
            return self.evid_link_template.copy()
        else:
            return None

    def get_agent_name(self, template_name):
        template_name = template_name.lower()
        if "evid" in template_name:
            return self.evid_template["agent_name"]
        elif "link" in template_name:
            return self.evid_link_template["agent_name"]
        else:
            return None

    def get_agent_description(self, template_name):
        template_name = template_name.lower()
        if "evid" in template_name:
            return self.evid_template["agent_description"]
        elif "link" in template_name:
            return self.evid_link_template["agent_description"]
        else:
            return None

    def get_agent_knowledge_base(self, template_name):
        template_name = template_name.lower()
        if "evid" in template_name:
            return self.evid_template["knowledge"]
        elif "link" in template_name:
            return self.evid_link_template["knowledge"]
        else:
            return None

    def get_agent_iteration_num(self, template_name):
        template_name = template_name.lower()
        if "evid" in template_name:
            return self.evid_template["max_iterations"]
        elif "link" in template_name:
            return self.evid_link_template["max_iterations"]
        else:
            return None
class Task3Template():
    def __init__(self, template_dir="input_template"):
        self.exp_template = read_json(os.path.join(template_dir, "exp_gen_template.txt"))

    def get_template(self, template_name):
        template_name = template_name.lower()
        if "exp" in template_name:
            return self.exp_template.copy()
        else:
            return None

    def get_agent_name(self, template_name):
        template_name = template_name.lower()
        if "exp" in template_name:
            return self.exp_template["agent_name"]
        else:
            return None

    def get_agent_description(self, template_name):
        template_name = template_name.lower()
        if "exp" in template_name:
            return self.exp_template["agent_description"]
        else:
            return None

    def get_agent_knowledge_base(self, template_name):
        template_name = template_name.lower()
        if "exp" in template_name:
            return self.exp_template["knowledge"]
        else:
            return None

    def get_agent_iteration_num(self, template_name):
        template_name = template_name.lower()
        if "exp" in template_name:
            return self.exp_template["max_iterations"]
        else:
            return None