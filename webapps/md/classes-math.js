class Vector {
    constructor(x,y) {
        this.x = x;
        this.y = y;
    }
    
    mult_scalar_inplace(s) {
        this.x = s*this.x;
        this.y = s*this.y;
    }
    mult_scalar(s) {
        return new Vector(s*this.x, s*this.y);
    }

    sq() {
        return this.x*this.x + this.y*this.y;
    }
    norm() {
        return Math.sqrt(this.sq());
    }
    dot(vec) {
        return this.x*vec.x + this.y*vec.y;
    }

    add(vec) {
        return new Vector( this.x+vec.x, this.y+vec.y );
    }
    sub(vec) {
        return new Vector( this.x-vec.x, this.y-vec.y );
    }
    opposite() {
        return new Vector( -this.x, -this.y);
    }
    
    mic(L) { // Minimum Image Convenction
        var x = this.x, y = this.y;
        if      ( this.x >  0.5*L.x ) x = this.x - L.x;
        else if ( this.x < -0.5*L.x ) x = this.x + L.x;
        if      ( this.y >  0.5*L.y ) y = this.y - L.y;
        else if ( this.y < -0.5*L.y ) y = this.y + L.y;
        return new Vector( x, y );
    }
    
    add_inplace(vec) {
        this.x = this.x+vec.x;
        this.y = this.y+vec.y;
    }
    sub_inplace(vec) {
        this.x = this.x-vec.x;
        this.y = this.y-vec.y;
    }
    opposite_inplace() {
        this.x = -this.x;
        this.y = -this.y;
    }
    
    min() {
        if(this.x < this.y) return this.x;
        else                return this.y;
    }
    max() {
        if(this.x > this.y) return this.x;
        else                return this.y;
    }
    
    mic_inplace(L) { // Minimum Image Convenction
        if      ( this.x >  0.5*L.x ) this.x -= L.x;
        else if ( this.x < -0.5*L.x ) this.x += L.x;
        if      ( this.y >  0.5*L.y ) this.y -= L.y;
        else if ( this.y < -0.5*L.y ) this.y += L.y;
    }
}

// Generate two random Gaussian variables with  Marsaglia polar method
function Gaussian2D(mean, std) {
    var u,v,s;
    do {
        u = 2*Math.random() - 1.0; // uniform in (-1,1)
        v = 2*Math.random() - 1.0;
        s = u*u + v*v;
    } while (s >= 1);
    if(s!=0) { s = Math.sqrt( -2*Math.log(s) / s ); }
    return new Vector( mean + std*(u*s), mean + std*(v*s) );
}

