function _make_figures(plot_dir, fmt, name, wid, hgt, res, start_ind)
    %%%% Create figures in the given plot directory.
    %%%%

    handles = get(0, 'children');
    for ind = 1:length(handles)
        filename = sprintf('%s%03d', name, ind + start_ind);
        filepath = fullfile(plot_dir, [filename, '.', fmt]);
        pngpath = fullfile(plot_dir, [filename, '.png']);

        h = handles(ind);
        pos = get(h, 'position');
        % If no width or height is given, use the figure size.
        if (wid < 0 && hgt < 0 && res == 0)
          wid = pos(3);
          hgt = pos(4);
        % If no width is given, scale based on figure aspect.
        elseif (wid < 0)
          wid = pos(3) * hgt / pos(4);
        % If no height is given, scale based on figure aspect.
        elseif (hgt < 0)
          hgt = pos(4) * wid / pos(3);
        end;

        if (wid > 0)
          size_opt = sprintf('-S%d,%d', wid, hgt);
        else 
          size_opt = sprintf('-r%d', res);
        end

        % Try to use imwrite if the figure only contains an image
        % with no title or labels.
        im = check_imwrite(h);

        if (im)
            try
               % Try to save the image.
               save_image(im, pngpath);
            catch
               % Fall back on a standard figure save.
               safe_print(h, filepath, pngpath, size_opt);
            end;
        else
            safe_print(h, filepath, pngpath, size_opt);
        end;
        close(h);
    end;
end;


function im = check_imwrite(h)
  im = '';

  if (length(get(h, 'children')) != 1)
    return;
  end;

  ax = get(h, 'children');

  if (length(get(ax, 'children')) != 1)
    return;
  end;

  artist = get(ax, 'children');

  if (strcmp(get(artist, 'type'), 'image') != 1)
    return;
  end;

  if (get(get(ax, 'title'), 'string'))
    return;
  end;

  if (get(get(ax, 'xlabel'), 'string'))
    return;
  end;

  if (get(get(ax, 'ylabel'), 'string'))
    return;
  end;

  % Check for image too small to display
  cdata = get(artist, 'cdata');
  if (size(cdata)(1) < 100 || size(cdata)(2) < 100)
    return;
  end;

  im = artist;
end;


function save_image(im, pngpath) 
  cdata = double(get(im, 'cdata'));

  if (ndims(cdata) == 2)
    mapping = get(im, 'cdatamapping');
    if (strcmp(mapping, 'scaled') == 1)
      clim = get(im, 'clim');
      cdata = cdata - clim(1);
      cdata = cdata ./ (clim(2) - clim(1));
    end;

    cmap = colormap(get(im, 'parent'));
    [I, ~] = gray2ind(cdata, length(cmap));
    imwrite(I, cmap, pngpath);

  else
    imwrite(cdata, pngpath);
  end;

end;


function safe_print(h, filepath, altpath, size_opt) 
  try 
    inner_print(h, filepath, size_opt);
  catch
    try
      inner_print(h, altpath, size_opt);
    catch ME
      close(h);
      error(ME.message);
    end
  end
end


function inner_print(h, filepath, size_opt)
  try
    print(h, filepath, size_opt);
  catch
    print(h, filepath);
  end
end
