import collections.abc
import json
import logging
import os

import numpy as np

logger = logging.getLogger(__name__)


class Settings(collections.abc.MutableMapping):
    def __init__(self):
        self._settings_dict = dict()
        self.settings_version = 1

    # Getters

    def __getitem__(self, key):
        # For convinience, this returns the Setting value and not the Setting object itself
        value = self.get_setting(key).value
        if value is not None:
            return value
        else:
            return self.get_default(key)

    def setting_exists(self, key):
        if key in self._settings_dict:
            return True
        else:
            return False

    def get_setting(self, key):
        if self.setting_exists(key):
            return self._settings_dict[key]
        else:
            return None

    def get_label(self, key):
        if self.setting_exists(key):
            return self.get_setting(key)._label
        else:
            return ''

    def get_default(self, key):
        if self.get_setting(key)._type == np.ndarray:
            return self.get_setting(key).default.copy()
        else:
            return self.get_setting(key).default

    def get_min_value(self, key):
        return self.get_setting(key).min_value

    def get_max_value(self, key):
        return self.get_setting(key).max_value

    def get_possible_values(self, key):
        return self.get_setting(key)._possible_values

    # Setters

    def __setitem__(self, key, value):
        # For convinience, this sets the Setting value and not a Setting object
        self.cast_and_set(key, value)

    def set_min_value(self, key, value):
        self.get_setting(key).min_value = value

    def set_max_value(self, key, value):
        self.get_setting(key).max_value = value

    def cast_and_set(self, key, value):
        # if len(value) == 0:
        #    return
        setting_type = self.get_setting(key)._type
        try:
            if setting_type is bool:
                value = bool(value)
            elif setting_type is int:
                value = int(value)
            elif setting_type is float:
                value = float(value)
            elif setting_type is str:
                value = str(value)
            elif setting_type is list:
                value = value
            elif setting_type is np.ndarray:
                value = np.asarray(value)
        except Exception:
            logger.error('Unable to cast setting %s to type %s' % (key, setting_type))
        else:
            self.get_setting(key).value = value

    # File management

    def load_settings(self, filepath=None, categories=None):
        from ferret_scan.settings.paths import get_base_path

        if filepath is None:
            filepath = os.path.join(get_base_path(), 'settings.json')
        with open(filepath) as f:
            self._load_json_dict(json.loads(f.read()), categories)

    def _load_json_dict(self, json_dict, categories):
        for category in json_dict.keys():
            if category == 'settings_version':
                continue
            if categories is None or category in categories:
                for key in json_dict[category]:
                    if key in self._settings_dict:
                        self._convert_to_type(key, json_dict[category][key])
                        self.get_setting(key)._load_json_dict(json_dict[category][key])

    def _convert_to_type(self, key, json_dict):
        if self._settings_dict[key]._type == np.ndarray:
            json_dict['value'] = np.asarray(json_dict['value'])

    def save_settings(self, filepath=None, categories=None):
        from ferret_scan.settings.paths import get_base_path

        if filepath is None:
            filepath = os.path.join(get_base_path(), 'settings.json')

        # If trying to overwrite some categories of settings.json, first load it
        # to preserve the other values
        if categories is not None and filepath == os.path.join(get_base_path(), 'settings.json'):
            with open(filepath) as f:
                initial_json = json.loads(f.read())
        else:
            initial_json = None

        with open(filepath, 'w') as f:
            f.write(json.dumps(self._to_json_dict(categories, initial_json), sort_keys=True, indent=4))
        logger.info(f'Saving settings to {filepath}')

    def _to_json_dict(self, categories, initial_json=None):
        if initial_json is None:
            json_dict = dict()
        else:
            json_dict = initial_json.copy()

        json_dict['settings_version'] = self.settings_version
        for key in self._settings_dict.keys():
            cur_setting = self.get_setting(key)
            if categories is not None and cur_setting._category not in categories:
                continue
            # hack to use panel add_control()
            if cur_setting._category == 'no_settings':
                continue
            if cur_setting._category not in json_dict:
                json_dict[cur_setting._category] = dict()
                # print "Profile category {0}".format(cur_setting._category)
            json_dict[cur_setting._category][key] = cur_setting._to_json_dict()
        return json_dict

    # Other

    def __delitem__(self, key):
        del self._settings_dict[key]

    def __iter__(self):
        return iter(self._settings_dict)

    def __len__(self):
        return len(self._settings_dict)

    def reset_to_default(self, key=None, categories=None):
        if key is not None:
            self.__setitem__(key, self.get_default(key))
        else:
            for key in self._settings_dict.keys():
                if categories is not None and self.get_setting(key)._category not in categories:
                    continue
                self.__setitem__(key, self.get_default(key))

    def _add_setting(self, setting):
        if setting._id not in self._settings_dict:
            self._settings_dict[setting._id] = setting

    def _initialize_settings(self):
        from ferret_scan.settings.registry import run_registered

        run_registered(self)


class Setting:
    def __init__(
        self,
        setting_id,
        label,
        category,
        setting_type,
        default,
        min_value=None,
        max_value=None,
        possible_values=None,
        tooltip='',
        tag=None,
    ):
        self._id = setting_id
        self._label = label
        self._category = category
        self._type = setting_type
        self._tooltip = tooltip
        self._tag = tag

        self.min_value = min_value
        self.max_value = max_value
        self._possible_values = possible_values
        self.default = default
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            return
        self._check_type(value)
        value = self._check_range(value)
        value = self._check_possible_values(value)
        self.__value = value

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, value):
        self._check_type(value)
        value = self._check_range(value)
        value = self._check_possible_values(value)
        self.__default = value

    @property
    def min_value(self):
        return self.__min_value

    @min_value.setter
    def min_value(self, value):
        if value is not None:
            self._check_type(value)
        self.__min_value = value

    @property
    def max_value(self):
        return self.__max_value

    @max_value.setter
    def max_value(self, value):
        if value is not None:
            self._check_type(value)
        self.__max_value = value

    def _check_type(self, value):
        if not isinstance(value, self._type):
            from ferret_scan.settings.paths import get_config_dir

            logger.error(
                'Error when setting %s.\n%s (%s) is not of type %s. '
                'Please remove current profile at %s' % (self._id, value, type(value), self._type, get_config_dir())
            )

    def _check_range(self, value):
        if self.min_value is not None and value < self.min_value:
            logger.warning('Warning: For setting %s, %s is below min value %s.' % (self._id, value, self.min_value))
            return self.min_value
        if self.max_value is not None and value > self.max_value:
            logger.warning('Warning: For setting %s.\n%s is above max value %s.' % (self._id, value, self.max_value))
            return self.max_value
        return value

    def _check_possible_values(self, value):
        if self._possible_values is not None and value not in self._possible_values:
            logger.error(
                'Error when setting %s.\n%s is not within the possible values %s.'
                % (self._id, value, self._possible_values)
            )
            if len(self._possible_values) > 0:
                return self._possible_values[0]
        return value

    def _load_json_dict(self, json_dict):
        # Only load configurable fields (__value, __min_value, __max_value)
        self.value = json_dict['value']
        if 'min_value' in json_dict:
            self.min_value = json_dict['min_value']
        if 'max_value' in json_dict:
            self.max_value = json_dict['max_value']

    def _to_json_dict(self):
        # Convert only configurable fields
        json_dict = dict()

        if self.value is None:
            value = self.default
        else:
            value = self.value

        if self._type == np.ndarray and value is not None:
            json_dict['value'] = value.tolist()
        else:
            json_dict['value'] = value

        if self.min_value is not None:
            json_dict['min_value'] = self.min_value

        if self.max_value is not None:
            json_dict['max_value'] = self.max_value
        return json_dict


# Define a fake _() function to fake the gettext tools in to generating
# strings for the profile settings.
