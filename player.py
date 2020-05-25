from threading import Thread
import numpy as np
from queue import Queue
import time
import sounddevice as sd

WIDTH = 2
CHANNELS = 1
SAMPLE_RATE =44100
CHUNK_SIZE = int(SAMPLE_RATE *0.05)

class Player:
	def __init__(self):
		self.dur = 0.1
		self.done = False
		self.pos_queue = Queue()
		self.phase = 0
		self.note_buffer = None

		self.play_thread = Thread(target = self.run_sd)
		self.data_thread = Thread(target = self.handle_data)

	def start(self):
		self.data_thread.start()
		self.play_thread.start()

	def handle_data(self):
		while not self.done:
			data = self.pos_queue.get()
			self.pos_queue.queue.clear()
			note = self.pos_to_note_pentatonic(data)
			if note:
				self.note_buffer = self.synth_note(note)
			else:
				self.note_buffer = None

	def run_sd(self):
		while not self.done:
			if self.note_buffer is not None:
				sd.play(self.note_buffer, SAMPLE_RATE)
				sd.wait()

	def pos_to_note_pentatonic(self, x):
		#Rule for mapping absolute position to a note information
		min_x = 0
		max_x = 5
		base_note = 220 #A0
		num_octaves = 4

		scale=[0,3,5,7,10]

		exp_scale=[]
		for n in range(num_octaves):
			exp_scale.extend([p+12*n for p in scale])

		#map linear scale to log

		if x[1] > 1:
			note_idx = (x[0] - min_x) * num_octaves * len(scale) // max_x
			note = exp_scale[int(note_idx)]
			pitch = base_note * 2 ** (note/12)
			return pitch
		else:
			return 0
			
	def pos_to_note(self, x):
		#Rule for mapping absolute position to a note information
		min_x = 0
		max_x = 5
		base_note = 220 #A0
		num_octaves = 4

		#map linear scale to log

		if x[1] > 1:
			note = (x[0] - min_x) * num_octaves * 12 // max_x
			pitch = base_note * 2 ** (note/12)
			return pitch
		else:
			return 0

	def synth_note(self, pitch, dur = None):
		
		if dur is None:
			dur = self.dur
		
		#TODO : change the harmonics later based on other dimensions

		t = np.linspace(0, dur, int(dur * SAMPLE_RATE))
		sig = np.sin(2* np.pi * t * pitch + self.phase)
		self.phase += dur *2*np.pi * pitch
		sig = 0.8 *sig.astype(np.float32)
		
		return sig

	def __del__(self):
		print("Finished playing")
		self.done=False

if __name__ == '__main__':
	
	pl = Player()
	pl.start()

	for i in np.arange(1,4,0.1):
		pl.pos_queue.put((i,0,0))
