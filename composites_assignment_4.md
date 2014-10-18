

    %matplotlib inline
    from composites.sim import Sim,ureg,Q_
    from composites.laminate import Laminate
    import matplotlib.pyplot as plt
    import numpy as np


    #Create a Simulation object composed of a laminate.
    sim = Sim(laminate = Laminate('0_2/p25/0_2s',
                                   materialID = 5, #5
                                   core_thick = 0.01))

**Ply orientation list **


    print sim.laminate.print_orientation()

    Orientation [degrees] : 
    [0, 0, 25, -25, 0, 0, 0, 0, -25, 25, 0, 0]
    

**Number of plies **


    print sim.laminate.num_of_layers()

    12
    

**Material properties **


    params = sim.laminate.print_param()
    print params

    Graphite/Thermoplastic
    '          ID :                      5  [-]'
    'fiber/matrix :               AS4/PEEK  [-]'
    '        name : Graphite/Thermoplastic  [-]'
    '          ex :               134.0000  [GPA]'
    '          ey :                 8.9000  [GPA]'
    '          es :                 5.1000  [GPA]'
    '         nux :                 0.2800  [-]'
    '          xt :              2130.0000  [MPA]'
    '          xc :              1100.0000  [MPA]'
    '          yt :                80.0000  [MPA]'
    '          yc :               200.0000  [MPA]'
    '          sc :               160.0000  [MPA]'
    '          h0 :                 0.1250  [mm]'
    '         nuy :                 0.0186  [-]'
    
    

**Thickness**


    print "Total thickness : %7.6f [m]" % sim.laminate.total_thickness
    print "Ply thickness   : %7.6f [m]" % sim.laminate.total_ply_thickness

    Total thickness : 0.011500 [m]
    Ply thickness   : 0.001500 [m]
    

**On-axis Modulus and Compliance matrices -- [Q] and [S] **


    print sim.laminate.print_array('QSon',1)

    S_on [1/GPa] : 
    [[   0.0075   -0.0021    0.0000]
     [  -0.0021    0.1124    0.0000]
     [   0.0000    0.0000    0.1961]]
    U's for S [1/GPa]
    U1 :  0.0689
    U2 : -0.0524
    U3 : -0.0090
    U4 : -0.0111
    U5 :  0.1600
    
    Q_on [GPa] : 
    [[ 134.7014    2.5050    0.0000]
     [   2.5050    8.9466    0.0000]
     [   0.0000    0.0000    5.1000]]
    U's for Q [GPa]
    U1 : 57.0443
    U2 : 62.8774
    U3 : 14.7797
    U4 : 17.2848
    U5 : 19.8797
    
    
    
    

**In-plane Modulus and Compliance -- [A] and [a]**


    print sim.laminate.print_A()

    A [GN/m] : 
    [[   0.7526    0.1853    0.0000]
     [   0.1853    0.5864    0.0000]
     [   0.0000    0.0000    0.2151]]
    a [m/GN] : 
    [[   1.4408   -0.4552   -0.0000]
     [  -0.4552    1.8491   -0.0000]
     [   0.0000    0.0000    4.6486]]
    

**Flexural Modulus and Compliance -- [D] and [d]**


    print sim.laminate.print_D()

    D [kNm] : 
    [[   5.2718    0.3594    0.0130]
     [   0.3594    0.4622    0.0032]
     [   0.0130    0.0032    0.4720]]
    d [1/MNm] : 
    [[ 200.3143 -155.6995   -4.4529]
     [-155.6995 2284.5488  -11.2113]
     [  -4.4529  -11.2113 2118.8941]]
    


    #Define and apply load
    P = 225*98.1*ureg.N; L = 0.52*ureg.m
    b = 0.1*ureg.m; moment = -P*L/(4*b)
    M = Q_([moment.magnitude,0,0],moment.units)

**Loads**


    print "M [N] : "
    print M.magnitude
    print "\nN [N/m] : "
    print [0,0,0]

    M [N] : 
    [-28694.2500    0.0000    0.0000]
    
    N [N/m] : 
    [0, 0, 0]
    


    #Apply load
    sim.apply_M(M)

**Curvature**


    print "K [m] :"
    print sim.k

    K [m] :
    [  -5.7479    4.4677    0.1278]
    


    import sympy
    sympy.init_printing()


    #Require pandas 0.14.1+
    df = sim.return_results()
    df




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>$\epsilon_1$</th>
      <th>$\epsilon_2$</th>
      <th>$\epsilon_6$</th>
      <th>$\epsilon_x$</th>
      <th>$\epsilon_y$</th>
      <th>$\epsilon_s$</th>
      <th>$\sigma_1$</th>
      <th>$\sigma_2$</th>
      <th>$\sigma_6$</th>
    </tr>
    <tr>
      <th>Ply Number</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0 (0$^\circ$) - Bot</th>
      <td> 0.0331</td>
      <td>-0.0257</td>
      <td>-0.0007</td>
      <td> 0.0331</td>
      <td>-0.0257</td>
      <td>-0.0007</td>
      <td> 4.3876</td>
      <td>-0.1470</td>
      <td>-0.0037</td>
    </tr>
    <tr>
      <th>0 (0$^\circ$) - Top</th>
      <td> 0.0323</td>
      <td>-0.0251</td>
      <td>-0.0007</td>
      <td> 0.0323</td>
      <td>-0.0251</td>
      <td>-0.0007</td>
      <td> 4.2922</td>
      <td>-0.1438</td>
      <td>-0.0037</td>
    </tr>
    <tr>
      <th>1 (0$^\circ$) - Bot</th>
      <td> 0.0323</td>
      <td>-0.0251</td>
      <td>-0.0007</td>
      <td> 0.0323</td>
      <td>-0.0251</td>
      <td>-0.0007</td>
      <td> 4.2922</td>
      <td>-0.1438</td>
      <td>-0.0037</td>
    </tr>
    <tr>
      <th>1 (0$^\circ$) - Top</th>
      <td> 0.0316</td>
      <td>-0.0246</td>
      <td>-0.0007</td>
      <td> 0.0316</td>
      <td>-0.0246</td>
      <td>-0.0007</td>
      <td> 4.1968</td>
      <td>-0.1406</td>
      <td>-0.0036</td>
    </tr>
    <tr>
      <th>2 (25$^\circ$) - Bot</th>
      <td> 0.0316</td>
      <td>-0.0246</td>
      <td>-0.0007</td>
      <td> 0.0213</td>
      <td>-0.0143</td>
      <td>-0.0435</td>
      <td> 2.8346</td>
      <td>-0.0743</td>
      <td>-0.2218</td>
    </tr>
    <tr>
      <th>2 (25$^\circ$) - Top</th>
      <td> 0.0309</td>
      <td>-0.0240</td>
      <td>-0.0007</td>
      <td> 0.0208</td>
      <td>-0.0139</td>
      <td>-0.0425</td>
      <td> 2.7702</td>
      <td>-0.0726</td>
      <td>-0.2168</td>
    </tr>
    <tr>
      <th>3 (-25$^\circ$) - Bot</th>
      <td> 0.0309</td>
      <td>-0.0240</td>
      <td>-0.0007</td>
      <td> 0.0214</td>
      <td>-0.0145</td>
      <td> 0.0416</td>
      <td> 2.8397</td>
      <td>-0.0760</td>
      <td> 0.2123</td>
    </tr>
    <tr>
      <th>3 (-25$^\circ$) - Top</th>
      <td> 0.0302</td>
      <td>-0.0235</td>
      <td>-0.0007</td>
      <td> 0.0209</td>
      <td>-0.0141</td>
      <td> 0.0407</td>
      <td> 2.7737</td>
      <td>-0.0742</td>
      <td> 0.2073</td>
    </tr>
    <tr>
      <th>4 (0$^\circ$) - Bot</th>
      <td> 0.0302</td>
      <td>-0.0235</td>
      <td>-0.0007</td>
      <td> 0.0302</td>
      <td>-0.0235</td>
      <td>-0.0007</td>
      <td> 4.0060</td>
      <td>-0.1343</td>
      <td>-0.0034</td>
    </tr>
    <tr>
      <th>4 (0$^\circ$) - Top</th>
      <td> 0.0295</td>
      <td>-0.0229</td>
      <td>-0.0007</td>
      <td> 0.0295</td>
      <td>-0.0229</td>
      <td>-0.0007</td>
      <td> 3.9107</td>
      <td>-0.1311</td>
      <td>-0.0033</td>
    </tr>
    <tr>
      <th>5 (0$^\circ$) - Bot</th>
      <td> 0.0295</td>
      <td>-0.0229</td>
      <td>-0.0007</td>
      <td> 0.0295</td>
      <td>-0.0229</td>
      <td>-0.0007</td>
      <td> 3.9107</td>
      <td>-0.1311</td>
      <td>-0.0033</td>
    </tr>
    <tr>
      <th>5 (0$^\circ$) - Top</th>
      <td> 0.0287</td>
      <td>-0.0223</td>
      <td>-0.0006</td>
      <td> 0.0287</td>
      <td>-0.0223</td>
      <td>-0.0006</td>
      <td> 3.8153</td>
      <td>-0.1279</td>
      <td>-0.0033</td>
    </tr>
    <tr>
      <th>6 (0$^\circ$) - Bot</th>
      <td>-0.0287</td>
      <td> 0.0223</td>
      <td> 0.0006</td>
      <td>-0.0287</td>
      <td> 0.0223</td>
      <td> 0.0006</td>
      <td>-3.8153</td>
      <td> 0.1279</td>
      <td> 0.0033</td>
    </tr>
    <tr>
      <th>6 (0$^\circ$) - Top</th>
      <td>-0.0295</td>
      <td> 0.0229</td>
      <td> 0.0007</td>
      <td>-0.0295</td>
      <td> 0.0229</td>
      <td> 0.0007</td>
      <td>-3.9107</td>
      <td> 0.1311</td>
      <td> 0.0033</td>
    </tr>
    <tr>
      <th>7 (0$^\circ$) - Bot</th>
      <td>-0.0295</td>
      <td> 0.0229</td>
      <td> 0.0007</td>
      <td>-0.0295</td>
      <td> 0.0229</td>
      <td> 0.0007</td>
      <td>-3.9107</td>
      <td> 0.1311</td>
      <td> 0.0033</td>
    </tr>
    <tr>
      <th>7 (0$^\circ$) - Top</th>
      <td>-0.0302</td>
      <td> 0.0235</td>
      <td> 0.0007</td>
      <td>-0.0302</td>
      <td> 0.0235</td>
      <td> 0.0007</td>
      <td>-4.0060</td>
      <td> 0.1343</td>
      <td> 0.0034</td>
    </tr>
    <tr>
      <th>8 (-25$^\circ$) - Bot</th>
      <td>-0.0302</td>
      <td> 0.0235</td>
      <td> 0.0007</td>
      <td>-0.0209</td>
      <td> 0.0141</td>
      <td>-0.0407</td>
      <td>-2.7737</td>
      <td> 0.0742</td>
      <td>-0.2073</td>
    </tr>
    <tr>
      <th>8 (-25$^\circ$) - Top</th>
      <td>-0.0309</td>
      <td> 0.0240</td>
      <td> 0.0007</td>
      <td>-0.0214</td>
      <td> 0.0145</td>
      <td>-0.0416</td>
      <td>-2.8397</td>
      <td> 0.0760</td>
      <td>-0.2123</td>
    </tr>
    <tr>
      <th>9 (25$^\circ$) - Bot</th>
      <td>-0.0309</td>
      <td> 0.0240</td>
      <td> 0.0007</td>
      <td>-0.0208</td>
      <td> 0.0139</td>
      <td> 0.0425</td>
      <td>-2.7702</td>
      <td> 0.0726</td>
      <td> 0.2168</td>
    </tr>
    <tr>
      <th>9 (25$^\circ$) - Top</th>
      <td>-0.0316</td>
      <td> 0.0246</td>
      <td> 0.0007</td>
      <td>-0.0213</td>
      <td> 0.0143</td>
      <td> 0.0435</td>
      <td>-2.8346</td>
      <td> 0.0743</td>
      <td> 0.2218</td>
    </tr>
    <tr>
      <th>10 (0$^\circ$) - Bot</th>
      <td>-0.0316</td>
      <td> 0.0246</td>
      <td> 0.0007</td>
      <td>-0.0316</td>
      <td> 0.0246</td>
      <td> 0.0007</td>
      <td>-4.1968</td>
      <td> 0.1406</td>
      <td> 0.0036</td>
    </tr>
    <tr>
      <th>10 (0$^\circ$) - Top</th>
      <td>-0.0323</td>
      <td> 0.0251</td>
      <td> 0.0007</td>
      <td>-0.0323</td>
      <td> 0.0251</td>
      <td> 0.0007</td>
      <td>-4.2922</td>
      <td> 0.1438</td>
      <td> 0.0037</td>
    </tr>
    <tr>
      <th>11 (0$^\circ$) - Bot</th>
      <td>-0.0323</td>
      <td> 0.0251</td>
      <td> 0.0007</td>
      <td>-0.0323</td>
      <td> 0.0251</td>
      <td> 0.0007</td>
      <td>-4.2922</td>
      <td> 0.1438</td>
      <td> 0.0037</td>
    </tr>
    <tr>
      <th>11 (0$^\circ$) - Top</th>
      <td>-0.0331</td>
      <td> 0.0257</td>
      <td> 0.0007</td>
      <td>-0.0331</td>
      <td> 0.0257</td>
      <td> 0.0007</td>
      <td>-4.3876</td>
      <td> 0.1470</td>
      <td> 0.0037</td>
    </tr>
  </tbody>
</table>
</div>




    z = sim.laminate.z_array.flatten()


    # fig = plt.figure()
    # ax = plt.axes()
    # ax.plot(np.vstack(sim.on_strain)[:,0],z,'-bo')
    # ax.set_ylabel('Height');ax.set_xlabel('On-axis strain')
    # ax.set_title('Height vs on-axis strain' )
    # ax.plot([0.0,0.0],[-0.006,0.006],'--k')
    # # ax.grid(axis = 'x')
    # plt.show()

**Strain distribution**


    #http://matplotlib.org/examples/pylab_examples/broken_axis.html
    f,(ax,ax2) = plt.subplots(2,1,sharex=True)
    ax.plot(np.vstack(sim.on_strain)[:,0],z,'-bo')
    ax2.plot(np.vstack(sim.on_strain)[:,0],z,'-bo')
    ax.set_ylim(0.0049,0.006); ax2.set_ylim(-0.006,-0.0049)
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop='off')
    ax2.xaxis.tick_bottom()
    d = 0.01
    kwargs = dict(transform=ax.transAxes,color = 'k',clip_on = False)
    ax.plot((-d,+d),(-d,+d), **kwargs)      # top-left diagonal
    ax.plot((1-d,1+d),(-d,+d), **kwargs)    # top-right diagonal
    
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d,+d),(1-d,1+d), **kwargs)   # bottom-left diagonal
    ax2.plot((1-d,1+d),(1-d,1+d), **kwargs) # bottom-right diagonal
    
    ax.set_ylabel('Above core');ax2.set_xlabel('On-axis strain')
    ax2.set_ylabel('Below core')
    ax.set_title('Height vs on-axis strain' )
    plt.show()


![png](composites_assignment_4_files/composites_assignment_4_27_0.png)


**Maximum strain and deflection $\delta$**


    del_criterion = 0.5*10**-2; strain_criterion = 0.002


    delta = P*L**3/(48*b)*(sim.laminate.d[0,0]*10**-9)
    max_strain = df[u'$\epsilon_x$'].max()
    print "Maximum deflection [cm] : %.4f"% (delta.magnitude*100)
    if delta.magnitude > del_criterion:
        print "Too large!"
    else:
        print "Is fine."
    print "Maximum strain [-]      : %.4f" % max_strain
    if max_strain > strain_criterion:
        print "Too large!"
    else:
        print "Is fine."

    Maximum deflection [cm] : 12.9519
    Too large!
    Maximum strain [-]      : 0.0331
    Too large!
    


    


    


    
