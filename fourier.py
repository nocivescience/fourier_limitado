from manim import *
class FourierManim(Scene):
    CONFIG={
        'wait_time': 12,
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
        }
    }
    def construct(self):
        vectors= self.get_rotating_vectors()
        circles= self.get_circles(vectors)
        self.add(vectors,circles)
        self.wait(self.CONFIG['wait_time'])
    def get_freqs(self):
        n=self.CONFIG['n_vectors']
        return list(range(n//2,-n//2,-1))
    def get_coefficients(self):
        return list(complex(1).real for _ in range(self.CONFIG['n_vectors']))
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
        vector.set_length(vector.coeff)
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