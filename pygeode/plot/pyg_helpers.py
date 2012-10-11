# Shortcuts for plotting PyGeode vars
# Extends wrapper.py to automatically use information from the Pygeode Vars.

import wrappers as wr
import numpy as np

def _buildaxistitle(name = '', plotname = '', plottitle = '', plotunits = '', **dummy):
# {{{
  if name is None: name = ''
  if plotname is None: plotname = ''
  if plottitle is None: plottitle = ''
  if plotunits is None: plotunits = ''

  assert type(plotname) is str
  assert type(plottitle) is str
  assert type(plotunits) is str
  assert type(name) is str
  
  if plotname is not '': title = plotname # plotname is shorter, hence more suitable for axes
  elif plottitle is not '': title = plottitle
  elif name is not '': title = name
  else: title = ''

  if plotunits is not '': title += ' [%s]' % plotunits

  return title
# }}}

def _buildvartitle(axes = None, name = '', plotname = '', plottitle = '', plotunits = '', **dummy):
# {{{
  if name is None: name = ''
  if plotname is None: plotname = ''
  if plottitle is None: plottitle = ''
  if plotunits is None: plotunits = ''
  
  assert type(plotname) is str
  assert type(plottitle) is str
  assert type(plotunits) is str
  assert type(name) is str

  if plottitle is not '': title = plottitle # plottitle is longer, hence more suitable for axes
  elif plotname is not '': title = plotname
  elif name is not '': title = name
  else: title = 'Unnamed Var'

  if plotunits is not '': title += ' (%s)' % plotunits
    
  # Add information on degenerate axes to the title
  if axes is not None:
    for a in [a for a in axes if len(a) == 1]:
      title += ', ' + a.formatvalue(a.values[0])

  return title
# }}}

def scalevalues(var):
# {{{
   sf = var.plotatts.get('scalefactor', None)
   of = var.plotatts.get('offset', None)
   v = var.get().copy()
   if sf is not None: v *= sf
   if of is not None: v += of
   return v
# }}}

def axes_parm(axis):
# {{{
  vals = scalevalues(axis)
  lims = min(vals), max(vals)
  return axis.plotatts.get('plotscale', 'linear'), \
         _buildaxistitle(**axis.plotatts), \
         lims[::axis.plotatts.get('plotorder', 1)], \
         axis.formatter(), \
         axis.locator()
# }}}

def set_xaxis(axes, axis, lbl):
# {{{
  scale, label, lim, form, loc = axes_parm(axis)
  pl, pb, pr, pt = axes.pad
  if lbl:
     axes.setp(xscale = scale, xlabel = label, xlim = lim)
     axes.setp_xaxis(major_formatter = form, major_locator = loc)
     axes.pad = [pl, 0.25, pr, 0.3]
  else:
     axes.setp(xscale = scale, xlim = lim, xticklabels=[])
     axes.setp_xaxis(major_locator = loc)
     axes.pad = [pl, 0.1, pr, 0.3]
# }}}

def set_yaxis(axes, axis, lbl):
# {{{
  scale, label, lim, form, loc = axes_parm(axis)
  pl, pb, pr, pt = axes.pad
  if lbl:
     axes.setp(yscale = scale, ylabel = label, ylim = lim)
     axes.setp_yaxis(major_formatter = form, major_locator = loc)
     axes.pad = [0.8, pb, 0.1, pt]
  else:
     axes.setp(yscale = scale, ylim = lim, yticklabels=[])
     axes.pad = [0.1, pb, 0.1, pt]
# }}}

def build_basemap(lons, lats, **kwargs):
# {{{
  prd = dict(projection = 'cyl', resolution = 'c')
  prd.update(kwargs.pop('map', {}))
  proj = prd['projection']
  bnds = {}

  if proj not in ['sinu', 'moll', 'hammer', 'npstere', 'spstere', 'nplaea', 'splaea', 'npaeqd', 'spaeqd', 'robin', 'eck4', 'kav7', 'mbtfpq']:
    bnds = {'llcrnrlat':lats.min(), 
            'urcrnrlat':lats.max(),
            'llcrnrlon':lons.min(),
            'urcrnrlon':lons.max()}

  if proj == 'npstere':
    bnds = {'boundinglat':20, 'lon_0':0}

  if proj == 'spstere':
    bnds = {'boundinglat':-20, 'lon_0':0}

  bnds.update(prd)
  prd.update(bnds)
  
  return wr.BasemapAxes(**prd)
# }}}

def decorate_basemap(axes, **kwargs):
# {{{
  # Add coastlines, meridians, parallels
  cld = {}
  merd = dict(meridians=[-180,-90,0,90,180,270,360],
              labels=[1,0,0,1])
  pard = dict(circles=[-90,-60,-30,0,30,60,90],
              labels=[1,0,0,1])

  cld.update(kwargs.pop('coastlines', {}))
  merd.update(kwargs.pop('meridians', {}))
  pard.update(kwargs.pop('parallels', {}))

  axes.drawcoastlines(**cld)
  axes.drawmeridians(**merd)
  axes.drawparallels(**pard)
# }}}

# Do a 1D line plot
def vplot(var, fmt='', axes=None, lblx=True, lbly=True, **kwargs):
# {{{
  ''' 
  Plot variable, showing a contour plot for 2d variables or a line plot for 1d variables.

  Parameters
  ----------
  var :  :class:`Var`
     The variable to plot. Should have either 1 or 2 non-degenerate axes.

  Notes
  -----
  This function is intended as the simplest way to display the contents of a variable,
  choosing appropriate parameter values as automatically as possible.
  '''

  Y = var.squeeze()
  assert Y.naxes == 1, 'Variable to plot must have exactly one non-degenerate axis.'
  X = Y.axes[0]

  # If a vertical axis is present transpose the plot
  from pygeode.axis import ZAxis
  if isinstance(X, ZAxis):
    X, Y = Y, X

  x = scalevalues(X)
  y = scalevalues(Y)

  axes = wr.plot(x, y, fmt, axes=axes, **kwargs)

  # Apply the custom axes args
  axes.pad = (0.1, 0.1, 0.1, 0.1)
  set_xaxis(axes, X, lblx)
  set_yaxis(axes, Y, lbly)
  lbl = _buildvartitle(var.axes, var.name, **var.plotatts)
  axes.setp(title=lbl, label=lbl)

  return axes
# }}}

# Do a 2D contour plot
def vcontour(var, clevs=None, clines=None, axes=None, lblx=True, lbly=True, label=True, transpose=None, **kwargs):
# {{{
  Z = var.squeeze()
  assert Z.naxes == 2, 'Variable to contour must have two non-degenerate axes.'
  X, Y = Z.axes

  # If a vertical axis is present transpose the plot
  from pygeode.axis import ZAxis, Lat, Lon
  if transpose is None:
    if isinstance(X, ZAxis):
      X, Y = Y, X
    if isinstance(X, Lat) and isinstance(Y, Lon):
      X, Y = Y, X
  elif transpose:
    X, Y = Y, X

  x = scalevalues(X)
  y = scalevalues(Y)
  z = scalevalues(Z.transpose(Y, X))

  if axes is None: 
    if isinstance(X, Lon) and isinstance(Y, Lat):
      axes = build_basemap(x, y, **kwargs)
    else:
      axes = wr.AxesWrapper()

  if clevs is None and clines is None: 
    # If both clevs and clines are None, use default
    axes.contourf(x, y, z, 21, **kwargs)

  if not clevs is None:
    axes.contourf(x, y, z, clevs, **kwargs)
    # Special case; if plotting both filled and unfilled contours
    # with a single call, set the color of the latter to black
    kwargs['colors'] = 'k'
    kwargs['cmap'] = None

  if not clines is None:
    axes.contour(x, y, z, clines, **kwargs)

  if isinstance(axes, wr.BasemapAxes):
    decorate_basemap(axes, **kwargs)

  # Apply the custom axes args
  if label:
    axes.pad = (0.1, 0.1, 0.1, 0.1)
    set_xaxis(axes, X, lblx)
    set_yaxis(axes, Y, lbly)
    axes.setp(title = _buildvartitle(var.axes, var.name, **var.plotatts))

  return axes
# }}}

# Do a 2D contour plot
def vsigmask(var, axes, mjsig=0.9, mjc='0.8', mjalpha=1., mnsig=None, mnc='0.9', mnalpha=1., transpose=None):
# {{{
  Z = var.squeeze()
  assert Z.naxes == 2, 'Variable to contour must have two non-degenerate axes.'
  X, Y = Z.axes

  # If a vertical axis is present transpose the plot
  from pygeode.axis import ZAxis, Lat, Lon
  if transpose is None:
    if isinstance(X, ZAxis):
      X, Y = Y, X
    if isinstance(X, Lat) and isinstance(Y, Lon):
      X, Y = Y, X
  elif transpose:
    X, Y = Y, X

  x = scalevalues(X)
  y = scalevalues(Y)
  z = scalevalues(Z.transpose(Y, X))

  if mnsig is None:
    cl = [-1.1, -mjsig, mjsig, 1.1]
    clr = ['w', mjc, 'w']
    axes.contourf(x, y, z, cl, colors=clr, zorder=-1)
    cnt = axes.plots[-1]
    axes.modifycontours(cnt, ind=[0, 2], visible=False)
    axes.modifycontours(cnt, ind=[1], edgecolor='none', alpha=mjalpha)
  else:
    cl = [-1.1, -mnsig,-mjsig, mjsig, mnsig, 1.1]
    clr = ['w', mnc, mjc, mnc, 'w']
    axes.contourf(x, y, z, cl, colors=clr, zorder=-1)
    cnt = axes.plots[-1]
    axes.modifycontours(cnt, ind=[0,4], visible=False)
    axes.modifycontours(cnt, ind=[1,3], edgecolor='none', alpha=mnalpha)
    axes.modifycontours(cnt, ind=[2], edgecolor='none', alpha=mjalpha)

  return axes
# }}}

# Generic catch all interface (plotvar replacement)
def showvar(var, **kwargs):
# {{{
  ''' 
  Plot variable, showing a contour plot for 2d variables or a line plot for 1d variables.

  Parameters
  ----------
  var :  :class:`Var`
     The variable to plot. Should have either 1 or 2 non-degenerate axes.

  Notes
  -----
  This function is intended as the simplest way to display the contents of a variable,
  choosing appropriate parameter values as automatically as possible.
  '''

  Z = var.squeeze()
  assert Z.naxes in [1, 2], 'Variable %s has %d non-generate axes; must have 1 or 2.' % (var.name, Z.naxes)

  fig = kwargs.pop('fig', None)

  if Z.naxes == 1:
    ax = vplot(var, **kwargs)

  elif Z.naxes == 2:
    ax = vcontour(var, **kwargs)

    cbar = kwargs.pop('colorbar', dict(orientation='vertical'))
    cf = ax.find_plot(wr.Contourf)
    if cbar and cf is not None:
      ax = wr.colorbar(ax, cf, **cbar)

  import pylab as pyl
  if pyl.isinteractive():
    ax.render(fig)
  return ax
# }}}

def showcol(vs, size=(4.1,2), **kwargs):
# {{{
  ''' 
  Plot variable, showing a contour plot for 2d variables or a line plot for 1d variables.

  Parameters
  ----------
  v :  list of lists of :class:`Var`
     The variables to plot. Should have either 1 or 2 non-degenerate axes.

  Notes
  -----
  This function is intended as the simplest way to display the contents of a variable,
  choosing appropriate parameter values as automatically as possible.
  '''

  Z = [v.squeeze() for v in vs]

  assert Z[0].naxes in [1, 2], 'Variables %s has %d non-generate axes; must have 1 or 2.' % (Z.name, Z.naxes)

  for z in Z[1:]:
    assert Z[0].naxes == z.naxes, 'All variables must have the same number of non-generate dimensions'
    #assert all([a == b for a, b in zip(Z[0].axes, z.axes)])

  fig = kwargs.pop('fig', None)

  if Z[0].naxes == 1:
    axs = []
    ydat = []
    for v in vs:
      lblx = (v is vs[-1])
      ax = vplot(v, lblx = lblx, **kwargs)
      ax.size = size
      axs.append([ax])
      ydat.append(ax.find_plot(wr.Plot).plot_args[1])

    Ax = wr.grid(axs)
    ylim = (np.min([np.min(y) for y in ydat]), np.max([np.max(y) for y in ydat]))
    Ax.setp(ylim = ylim, children=True)

  elif Z[0].naxes == 2:
    axs = []
    for v in vs:
      lblx = (v is vs[-1])
      ax = vcontour(v, lblx = lblx, **kwargs)
      ax.size = size
      axs.append([ax])

    Ax = wr.grid(axs)

    cbar = kwargs.pop('colorbar', dict(orientation='vertical'))
    cf = Ax.axes[0].find_plot(wr.Contourf)
    if cbar and cf is not None:
      Ax = wr.colorbar(Ax, cf, **cbar)

  import pylab as pyl
  if pyl.isinteractive(): Ax.render(fig)
  return Ax
# }}}

def showgrid(vf, vl=[], ncol=1, size=(3.5,1.5), **kwargs):
# {{{
  ''' 
  Plot contours

  Parameters
  ----------
  v :  list of lists of :class:`Var`
     The variables to plot. Should have either 1 or 2 non-degenerate axes.

  Notes
  -----
  This function is intended as the simplest way to display the contents of a variable,
  choosing appropriate parameter values as automatically as possible.
  '''

  from pygeode import Var
  if isinstance(vf, Var): vf = [vf]
  if isinstance(vl, Var): vl = [vl]

  assert all([v.squeeze().naxes == 2 for v in vf]), 'Variables (vf) should have 2 degenerate axes.'
  nVf = len(vf)

  assert all([v.squeeze().naxes == 2 for v in vl]), 'Variables (vl) should have 2 degenerate axes.'
  nVl = len(vl)
  if nVf > 1 and nVl > 1: assert nVl == nVf, 'Must have the same number of filled and contour-line variables.'
    
  fig = kwargs.pop('fig', None)
  cbar = kwargs.pop('colorbar', dict(orientation='vertical'))
  xpad = 0.
  ypad = 0.

  kwlines = {}
  if nVl > 0:
    kwlines['colors'] = kwargs.pop('colors', 'k')
    kwlines['clines'] = kwargs.pop('clines', 11)
    for k in ['linewidths', 'linestyles']:
      if kwargs.has_key(k): kwlines[k] = kwargs.pop(k)

  kwfill = {}
  if nVf > 0:
    kwfill['clevs'] = kwargs.pop('clevs', 31)
    kwfill['cmap'] = kwargs.pop('cmap', None)
    kwlines['label'] = False
    if cbar: 
      if cbar.get('orientation', 'vertical') == 'vertical':
        ypad = cbar.get('width', 0.8)
      else:
        xpad = cbar.get('height', 0.4)

  
  kwcb = {}

  nV = max(nVl, nVf)
  nrow = np.ceil(nV / float(ncol))

  axpad = 0.2
  axpadl = 0.9
  aypad = 0.4
  aypadl = 0.55
  axw, axh = size
  ypad = ypad + aypadl + aypad * (nrow-1)
  xpad = xpad + axpadl + axpad * (ncol-1)

  axs = []
  row = []
  for i in range(nV):
    lblx = (i / ncol == nrow - 1)
    lbly = (i % ncol == 0)
    ax = None
    if nVf > 0: 
      v = vf[i % nVf]
      kwfill.update(kwargs)
      ax = vcontour(v, axes=ax, lblx = lblx, lbly = lbly, **kwfill)
    if nVl > 0:
      v = vl[i % nVl]
      kwlines.update(kwargs)
      ax = vcontour(v, axes=ax, lblx = lblx, lbly = lbly, **kwlines)

    if lblx: h = axh + aypadl
    else: h = axh + aypad
    if lbly: w = axw + axpadl
    else: w = axw + axpad

    ax.size = (w, h)
    row.append(ax)
    if i % ncol == ncol - 1:
      axs.append(row)
      row = []

  if len(row) > 0: 
    row.extend([None] * (ncol - len(row)))
    axs.append(row)

  Ax = wr.grid(axs)

  cf = Ax.axes[0].find_plot(wr.Contourf)
  if cbar and cf is not None:
    Ax = wr.colorbar(Ax, cf, **cbar)

  import pylab as pyl
  if pyl.isinteractive(): Ax.render(fig)
  return Ax
# }}}

def savepages(figs, fn, psize='A4', marg=0.5, scl=1.):
# {{{
  sizes = dict(A4 = (8.3, 11.7),
              A4l = (11.7, 8.3))
  if sizes.has_key(psize):
    pwidth, pheight = sizes[psize]
  else:
    pwidth, pheight = psize

  hmarg = marg
  wmarg = marg
  psize = (pwidth, pheight)

  fwidth = pwidth - 2*wmarg
  fheight = pheight - 2*hmarg

  ymarg = hmarg/pheight
  xmarg = wmarg/pwidth

  y = 1. - ymarg
  x = xmarg

  ax = wr.AxesWrapper(size=psize)
  from matplotlib.backends.backend_pdf import PdfPages
  pp = PdfPages(fn)

  page = 1
  nfigs = 0
  hlast = 0
  for f in figs:
    w = f.size[0] / pwidth * scl
    h = f.size[1] / pheight * scl

    if x + w < 1. - xmarg:
      r = [x, y - h, x + w, y]
      ax.add_axis(f, r)
      x += w
      hlast = max(h, hlast)
      nfigs += 1
    else:
      x = xmarg
      y = y - hlast

      if nfigs > 0 and y - h < ymarg:
        fig = ax.render('page%d' % page)
        pp.savefig(fig)
        ax = wr.AxesWrapper(size=psize)
        y = 1. - ymarg
        print 'Page %d, %d figures.' % (page, nfigs)
        page += 1
        nfigs = 0

      r = [x, y - h, x + w, y]
      ax.add_axis(f, r)
      x = x + w
      hlast = h
      nfigs += 1

  print 'Page %d, %d figures.' % (page, nfigs)
  fig = ax.render('page%d'%page, show=False)
  pp.savefig(fig)
  pp.close()
# }}}

__all__ = ['showvar', 'showcol', 'showgrid', 'vplot', 'vcontour', 'vsigmask', 'savepages']