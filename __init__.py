# Copyright 2021 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from os.path import dirname, basename
import glob
import random
import re

from mycroft.skills.audioservice import AudioService
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
import mycroft.audio


class AnimalSay(MycroftSkill):
    def __init__(self):
        super(AnimalSay, self).__init__(name="AnimalSay")
        self.animals = {}
        dirRoot = dirname(__file__)
        self.log.debug('root: ' + dirRoot)
        allFiles = glob.glob(dirRoot + '/*.wav')
        p = re.compile('^(.+)-[0-9]+\.wav$')
        for fp in allFiles:
            self.log.debug('trying file: ' + fp)
            result = p.search(basename(fp))
            if result is None:
                self.log.debug(fp + ' not matching')
                continue
            animalName = result.group(1)
            if animalName not in self.animals:
                self.animals[animalName] = []
            self.animals[animalName].append(fp)
            self.log.debug('Appending ' + fp + ' to ' + animalName + ' dict.')

    def initialize(self):
        self.register_intent_file("what.does.it.say.intent",
                                  self.handle_what_does_the_animal_say)
        self.register_intent_file("imitate.animal.intent",
                                  self.handle_imitate_animal)
        self.audioservice = AudioService(self.bus)

    def handle_what_does_the_animal_say(self, message):
        animal = message.data['animal']
        animalAlias = self.translate_namedvalues('animal.alias')
        animalImitate = self.translate_namedvalues('animal.imitate')
        if animal not in animalAlias or animalAlias[animal] not in animalImitate:
            self.speak_dialog('unknown.animal', {'animal': animal})
            return
        animalSound = animalImitate[animalAlias[animal]]
        self.speak_dialog('animal.says', {'animal': animalAlias[animal], 'sound': animalSound})

    def handle_imitate_animal(self, message):
        animal = message.data['animal']
        animalAlias = self.translate_namedvalues('animal.alias')
        animalCodes = self.translate_namedvalues('animal.sound')
        if animal not in animalAlias or animalAlias[animal] not in animalCodes:
            self.speak_dialog('unknown.animal', {'animal': animal})
            return
        animalCode = animalCodes[animalAlias[animal]]
        try:
            self.speak_dialog('animal.sounds.like', {'animal': animalAlias[animal]})
            mycroft.audio.wait_while_speaking()
            soundPath = random.choice(self.animals[animalCode])
            self.audioservice.play(soundPath)
        except Exception as e:
            self.log.error("Error: {0}".format(e))


def create_skill():
    return AnimalSay()
