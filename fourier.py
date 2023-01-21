from manim import *
import itertools as it
import operator as op 
import functools as ft
class FourierManim(Scene):
    CONFIG={
        'wait_time': 122,
        'vector_config':{
            'max_tip_length_to_length_ratio':.25,
            'tip_length': 0.15,
            'stroke_width': 1.3
        },
        'vector_time':ValueTracker(0),
        'center_point':ORIGIN,
        'n_vectors':10,
        'circle_config':{
            'fill_opacity':0,
            'stroke_width':.2
        },
        'low_factor':0.5,
    }
    def construct(self):
        vectors= self.get_rotating_vectors()
        circles= self.get_circles(vectors)
        paths=self.get_drawn_path(vectors)
        copies_wave=self.get_y_component_wave(vectors)
        self.add(vectors,circles,paths,copies_wave)
        self.wait(self.CONFIG['wait_time'])
    def get_freqs(self):
        n=self.CONFIG['n_vectors']
        return list(np.linspace(0.3,1,n))
    def get_coefficients(self):
        n=self.CONFIG['n_vectors']
        return [complex(.3) for _ in range(n)]
    def get_rotating_vectors(self,freqs=None, coeffs=None):
        vectors=VGroup()
        self.center_tracker=VectorizedPoint(self.CONFIG['center_point'])
        if freqs is None:
            freqs=self.get_freqs()
        if coeffs is None:
            coeffs=self.get_coefficients()
        last_vector=None
        for freq, coeff in zip(freqs, coeffs):
            if last_vector:
                center_func= last_vector.get_end
            else:
                center_func=self.center_tracker.get_location
            vector=self.get_rotating_vector(coeff,freq,center_func)
            vectors.add(vector)
            last_vector=vector
        return vectors
    def get_rotating_vector(self,coeff,freq,center_func):
        vector=Vector(**self.CONFIG['vector_config'])
        vector.coeff=coeff
        vector.freq=freq
        vector.center_func=center_func
        vector.scale(2)
        vector.add_updater(self.update_vector)
        return vector
    def update_vector(self,vector,dt):
        time=self.CONFIG['vector_time'].get_value()
        vector.set_length(vector.coeff.real)
        vector.rotate((time+dt)*vector.freq,about_point=vector.get_start())
        vector.shift(vector.center_func()-vector.get_start())
    def get_circle(self,vector,color=None):
        if color is None:
            color=RED
        circle=Circle(color=color,**self.CONFIG['circle_config'])
        circle.func_center=vector.get_start
        circle.func_radius=vector.get_length
        circle.add_updater(self.update_circle)
        return circle
    def get_circles(self,vectors):
        return VGroup(*[
            self.get_circle(vector) for vector in vectors
        ])
    def update_circle(self,circle):
        circle.set_width(2*circle.func_radius())
        circle.move_to(circle.func_center())
        return circle
    def get_vector_sum_path(self,vectors,color=YELLOW):
        coeffs=[v.coeff for v in vectors]
        freqs=[v.freq for v in vectors]
        center=vectors[0].get_start()
        path=ParametricFunction(
            lambda t: center+ ft.reduce(op.add,[complex_to_R3(coeff*np.exp(TAU*1j*freq*t))
                for coeff,freq in zip(coeffs, freqs)                                                  
            ]),
            t_range=[0,1]
        )
        return path
    def get_drawn_path(self,vectors,**kwargs):
        path=self.get_vector_sum_path(vectors)
        broken_path=CurvesAsSubmobjects(path)
        broken_path.curr_time=0
        start, end=[0,1]
        def update_path(path,dt):
            alpha=self.CONFIG['vector_time'].get_value()
            n_curves=len(path)
            for a, sp in zip(np.linspace(0,1,n_curves), path):
                b= (alpha-a)
                if b<0:
                    width=0
                else:
                    width=2*interpolate(
                        start,end, (1-(b%1))
                    )
                sp.set_stroke(width=width)
            path.curr_time+=dt
            return path
        broken_path.set_color(YELLOW_B)
        broken_path.add_updater(update_path)
        return broken_path
    