# -*- coding: utf-8 -*-
from cms.models.pluginmodel import CMSPlugin


class MPPath(object):
    def __init__(self, model):
        self.model = model
        self.model = CMSPlugin

    def max_root_path(self):
        self.model.get_last_root_node().path
