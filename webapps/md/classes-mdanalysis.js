// must be imported after 'classes-md.js'
System.prototype.start_RDF = function(nbins) {
  this.startedRDF = true;
  this.rdf = new Float32Array(nbins);
  this.num_rdf = 1;
}
System.prototype.computeRDF = function(nbins) {
    //if( typeof(nbins) !== "number" ) { throw Error('ERROR: Incorrect type for nbins.'); }
    let binsize = (0.5*this.L.min())/nbins;
    var i,j, k;
    var gr = new Float32Array(nbins);
    for( i=0; i<this.N; i++ )
    {
        for( j=i+1; j<this.N; j++ )
        {
            let rij = ( this.ps[i].pos.sub(this.ps[j].pos) ).mic(this.L);
            k = Math.floor( rij.norm() / binsize );
            if(k<nbins) gr[k] += 1.0;
        }
    }
    var shell1 = 0.0, shell2, r;
    let normalization = (this.N-1)/this.Volume() * 3.141592 * this.N/2.0;
    for( k=0; k<nbins; k++)
    {
        r = (k+1)*binsize;
        shell2 = r*r;
        gr[k] /= ( normalization * (shell2-shell1) );
        shell1 = shell2;
        // average over samples
        this.rdf[k] =(this.rdf[k]*(this.num_rdf-1) + gr[k] )/this.num_rdf ;
    }
    this.gr = gr;
    this.num_rdf+=1;
}


System.prototype.InitStructureFactor = function(npoints) {
  this.startedSq = true;
  this.num_sq = 1;
  this.sq2D = new Float32Array(npoints*npoints);
  this.sq = new Float32Array(npoints); // this is averaged over directions (nx,ny) such that n_prev < sqrt(nx^2+ny^2) < n
  this.sqcounter = new Float32Array(npoints);
  for(let i=0;i<npoints*npoints;i++) {
    this.sq2D[i] = 0.0;
    if(i<npoints) {
      this.sq[i] = 0.0;
      this.sqcounter[i] = 0;
    }
  }
}

System.prototype.computeSq = function(npoints) {
   // q = (1,2,...,nmax)*dq along each component
    let dqx = 2*3.141592 / this.L.x;
    let dqy = 2*3.141592 / this.L.y;
    let dq = Math.sqrt(dqx*dqy); // how do I take into account for non-cubic boxes?
    var i,j, nx,ny, n, re, idx2D;
    
    this.sq2D_now = new Float32Array(npoints*npoints);
    this.sq_now = new Float32Array(npoints);
    for(let i=0;i<npoints*npoints;i++) {
      this.sq2D_now[i] = 1.0; // initialize on diagonal part i==j
      if(i<npoints) {
        this.sq_now[i] = 0.0;
        this.sqcounter[i] = 0;
      }
    }

    for( nx=0; nx<npoints; nx++ )
    {
        for( ny=0; ny<npoints; ny++ )
        {
            for( i=0; i<this.N; i++)
            {
              for(j=i+1; j<this.N; j++)
              {
                let rij = ( this.ps[i].pos.sub(this.ps[j].pos) ).mic(this.L);
                re = Math.cos( nx*dqx*rij.x + ny*dqy*rij.y ) / this.N;
                idx2D = nx*npoints + ny;
                this.sq2D_now[ idx2D ] += 2*re; // imaginary part is zero; count twice the particles
              }
            }
            // average 2D spherically into 1D
            n = Math.floor(Math.sqrt(nx*nx + ny*ny) );
            if(n>0 && n<npoints)
            {
              this.sqcounter[n] ++;
              this.sq_now[n] += this.sq2D_now[ idx2D ];
            }
            // average over samples
            this.sq2D[idx2D] = (this.sq2D[idx2D]*(this.num_sq-1) + this.sq2D_now[idx2D] )/this.num_sq ;
        }
    }
    for(n=0;n<npoints;n++)
    {
      // average over wavevectors
      this.sq_now[n] /= this.sqcounter[n];
      // average over samples
      this.sq[n] = (this.sq[n]*(this.num_sq-1) + this.sq_now[n] )/this.num_sq ;
    }
    this.num_sq+=1;
}
